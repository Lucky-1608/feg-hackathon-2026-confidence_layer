"""Checkpoint model, processed rewards and offsets together before Kafka commit."""

import asyncio
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import OffsetAndMetadata, TopicPartition

from confidence.application.reward_join import RewardSignal
from confidence.config import load_config
from confidence.domain.ml.contextual_bandit import BanditPolicySelector
from confidence.infrastructure.model_registry import FileModelRegistry


class BanditTrainer:
    def __init__(self, policy: BanditPolicySelector, registry: FileModelRegistry) -> None:
        self.policy = policy
        self.registry = registry
        self.offsets: dict[str, int] = {}
        self.processed: set[str] = set()
        self.healthy = True
        self.pointer = registry.root / "trainer-current.json"
        if self.pointer.exists():
            state = json.loads(self.pointer.read_text())
            artifact = registry.root / ".staging" / state["artifact"]
            restored = BanditPolicySelector(str(artifact))
            if restored.model is None:
                raise RuntimeError("Checkpoint could not be restored")
            self.policy = restored
            self.offsets = state["offsets"]
            self.processed = set(state["processed"])

    def checkpoint(self, version: str) -> Path:
        if self.policy.model is None:
            raise RuntimeError("No trainable model")
        directory = self.registry.root / ".staging"
        directory.mkdir(parents=True, exist_ok=True)
        source = directory / f"{version}.vw"
        self.policy.model.save(str(source))
        with source.open("rb") as stream:
            os.fsync(stream.fileno())
        state = {"artifact": source.name, "offsets": self.offsets, "processed": sorted(self.processed)}
        temporary = self.pointer.with_suffix(".tmp")
        with temporary.open("w") as stream:
            json.dump(state, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.pointer)
        descriptor = os.open(self.registry.root, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return source

    async def process(self, consumer: Any, message: Any) -> None:
        if not self.healthy:
            raise RuntimeError("Restart from checkpoint before retrying")
        partition = f"{message.topic}:{message.partition}"
        offset = max(message.offset + 1, self.offsets.get(partition, 0))
        if message.offset < self.offsets.get(partition, 0):
            await consumer.commit({TopicPartition(message.topic, message.partition): OffsetAndMetadata(offset, "")})
            return
        reward = RewardSignal.model_validate_json(message.value)
        if reward.outcome_id is None:
            raise ValueError("Reward must carry a durable outcome ID")
        receipt = str(reward.outcome_id)
        try:
            if receipt not in self.processed:
                if not self.policy.learn(reward):
                    raise RuntimeError("Learning failed; offset retained")
                self.processed.add(receipt)
            self.offsets[partition] = offset
            self.checkpoint(uuid4().hex)
        except Exception:
            self.healthy = False
            raise
        await consumer.commit({TopicPartition(message.topic, message.partition): OffsetAndMetadata(offset, "")})


async def run_trainer() -> None:
    from vowpalwabbit import Workspace

    config = load_config()
    policy = BanditPolicySelector(config.policy.bandit_model_path)
    if policy.model is None and config.policy.bandit_model_path is None:
        policy.model = Workspace(cb_explore_adf=True, epsilon=config.policy.bandit_exploration_rate, quiet=True)
    trainer = BanditTrainer(policy, FileModelRegistry())
    consumer = AIOKafkaConsumer(
        "confidence.rewards",
        bootstrap_servers=config.kafka.bootstrap_servers,
        group_id="confidence-bandit-trainer",
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        async for message in consumer:
            await trainer.process(consumer, message)
    finally:
        await consumer.stop()
        trainer.policy.inference.close()


if __name__ == "__main__":
    asyncio.run(run_trainer())
