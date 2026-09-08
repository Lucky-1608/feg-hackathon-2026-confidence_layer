import re

# 1. Update config.py
with open("src/confidence/config.py", "r") as f:
    config_content = f.read()

config_addition = """
@dataclass(frozen=True)
class RedisConfig:
    url: str = "redis://localhost:6379/0"

@dataclass(frozen=True)
class KafkaConfig:
    bootstrap_servers: str = "localhost:19092"
"""

config_content = config_content.replace(
    "@dataclass(frozen=True)\nclass AppConfig:",
    config_addition + "\n@dataclass(frozen=True)\nclass AppConfig:"
)

config_content = config_content.replace(
    "    server: ServerConfig = field(default_factory=ServerConfig)",
    "    server: ServerConfig = field(default_factory=ServerConfig)\n    redis: RedisConfig = field(default_factory=RedisConfig)\n    kafka: KafkaConfig = field(default_factory=KafkaConfig)"
)

config_content = config_content.replace(
    "        server=ServerConfig(\n            host=os.getenv(\"HOST\", \"0.0.0.0\"),\n            port=int(os.getenv(\"PORT\", \"8000\")),\n        ),",
    "        server=ServerConfig(\n            host=os.getenv(\"HOST\", \"0.0.0.0\"),\n            port=int(os.getenv(\"PORT\", \"8000\")),\n        ),\n        redis=RedisConfig(url=os.getenv(\"REDIS_URL\", \"redis://localhost:6379/0\")),\n        kafka=KafkaConfig(bootstrap_servers=os.getenv(\"KAFKA_BOOTSTRAP_SERVERS\", \"localhost:19092\")),\n"
)

with open("src/confidence/config.py", "w") as f:
    f.write(config_content)


# 2. Update event_processor.py
with open("src/confidence/application/event_processor.py", "r") as f:
    processor = f.read()

processor = processor.replace("updates = {}", "from typing import Any\n        updates: dict[str, Any] = {}")
with open("src/confidence/application/event_processor.py", "w") as f:
    f.write(processor)


# 3. Update event_bus.py
with open("src/confidence/infrastructure/event_bus.py", "r") as f:
    bus = f.read()

bus = bus.replace(
    "    async def publish(self, event: ConfidenceEvent) -> None:",
    "    async def start(self) -> None:\n        ...\n\n    async def stop(self) -> None:\n        ...\n\n    async def publish(self, event: ConfidenceEvent) -> None:"
)
bus = bus.replace(
    "    def __init__(self) -> None:\n        self.published_events: list[ConfidenceEvent] = []",
    "    def __init__(self) -> None:\n        self.published_events: list[ConfidenceEvent] = []\n\n    async def start(self) -> None:\n        pass\n\n    async def stop(self) -> None:\n        pass"
)

with open("src/confidence/infrastructure/event_bus.py", "w") as f:
    f.write(bus)

print("Fixes applied.")
