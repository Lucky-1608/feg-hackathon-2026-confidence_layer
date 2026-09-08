"""Experiment definitions and cached assignments; reads stay off the decision path."""

import math
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel, Field
from scipy.stats import t, ttest_ind
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncEngine

from confidence.db.schema import experiment_assignments, experiments, session_quality_scores
from confidence.domain.policy import PolicySelector
from confidence.domain.state import StateEstimator
from confidence.infrastructure.shadow_mode import stable_bucket


class ExperimentDefinition(BaseModel):
    experiment_id: UUID
    treatment_percentage: float = Field(default=50, ge=0, le=100, allow_inf_nan=False)
    treatment_policy: str = "deterministic"
    treatment_estimator: str = "rules"


class ExperimentResults(BaseModel):
    experiment_id: UUID
    treatment_sessions: int
    control_sessions: int
    sqs_difference: float | None = None
    confidence_interval: tuple[float, float] | None = None
    p_value: float | None = None


class ExperimentManager:
    def __init__(
        self, engine: AsyncEngine, policies: dict[str, PolicySelector] | None = None, estimators: dict[str, StateEstimator] | None = None
    ) -> None:
        self.engine = engine
        self.definitions: dict[UUID, ExperimentDefinition] = {}
        self.active: ExperimentDefinition | None = None
        self.available = True
        self.policies = {"deterministic": PolicySelector()} | (policies or {})
        self.estimators = {"rules": StateEstimator()} | (estimators or {})

    async def refresh(self) -> None:
        self.available = False
        async with self.engine.connect() as conn:
            rows = (await conn.execute(select(experiments).where(experiments.c.is_active.is_(True)))).mappings().all()
        if len(rows) > 1:
            raise ValueError("Overlapping active experiments are not supported")
        self.active = None
        for row in rows:
            definition = ExperimentDefinition(experiment_id=row["experiment_id"], **row["config"])
            if definition.treatment_policy not in self.policies or definition.treatment_estimator not in self.estimators:
                raise ValueError("Experiment refers to an unavailable variant")
            self.definitions[definition.experiment_id] = definition
            self.active = definition
        self.available = True

    async def get_assignment(self, session_id: UUID, experiment_id: UUID) -> Literal["treatment", "control"]:
        definition = self.definitions[experiment_id]
        return "treatment" if stable_bucket(f"{experiment_id}:{session_id}") < definition.treatment_percentage else "control"

    async def create_experiment(self, name: str, description: str, experiment_type: str, config: dict[str, Any]) -> UUID:
        experiment_id = uuid4()
        definition = ExperimentDefinition(experiment_id=experiment_id, **{k: v for k, v in config.items() if k != "active"})
        if definition.treatment_policy not in self.policies or definition.treatment_estimator not in self.estimators:
            raise ValueError("Unknown experiment variant")
        async with self.engine.begin() as conn:
            await conn.execute(
                insert(experiments).values(
                    experiment_id=experiment_id,
                    name=name,
                    description=description,
                    experiment_type=experiment_type,
                    config=definition.model_dump(exclude={"experiment_id"}),
                    is_active=bool(config.get("active", False)),
                    created_at=datetime.now(UTC),
                )
            )
        self.definitions[experiment_id] = definition
        return experiment_id

    async def get_results(self, experiment_id: UUID) -> ExperimentResults:
        async with self.engine.connect() as conn:
            rows = (
                (
                    await conn.execute(
                        select(
                            experiment_assignments.c.session_id, experiment_assignments.c.assignment, session_quality_scores.c.clamped_score
                        )
                        .outerjoin(session_quality_scores, session_quality_scores.c.session_id == experiment_assignments.c.session_id)
                        .where(experiment_assignments.c.experiment_id == experiment_id)
                    )
                )
                .mappings()
                .all()
            )
        # Aggregate to the randomization unit; repeated decisions aren't independent samples.
        groups: dict[str, dict[UUID, list[float]]] = {"treatment": {}, "control": {}}
        for row in rows:
            values = groups[row["assignment"]].setdefault(row["session_id"], [])
            if row["clamped_score"] is not None:
                values.append(float(row["clamped_score"]))
        result = ExperimentResults(
            experiment_id=experiment_id, treatment_sessions=len(groups["treatment"]), control_sessions=len(groups["control"])
        )
        a, b = [np.array([np.mean(values) for values in groups[group].values() if values]) for group in ("treatment", "control")]
        if min(len(a), len(b)) < 2:
            return result
        delta = float(a.mean() - b.mean())
        v1, v2 = float(a.var(ddof=1) / len(a)), float(b.var(ddof=1) / len(b))
        if v1 + v2 == 0:
            # Constant samples do not justify a zero-width population uncertainty claim.
            result.sqs_difference = delta
            return result
        df = (v1 + v2) ** 2 / (v1 * v1 / (len(a) - 1) + v2 * v2 / (len(b) - 1))
        width = float(t.ppf(0.975, df)) * math.sqrt(v1 + v2)
        result.sqs_difference = delta
        result.confidence_interval = (delta - width, delta + width)
        result.p_value = float(ttest_ind(a, b, equal_var=False).pvalue)
        return result
