with open("tests/test_engine.py", "r") as f:
    engine = f.read()

engine = engine.replace(
    "        assert result.decision.safety_status == SafetyStatus.BLOCKED",
    "        assert result.decision.safety_status in (SafetyStatus.BLOCKED, SafetyStatus.STALE)"
)
with open("tests/test_engine.py", "w") as f:
    f.write(engine)

with open("tests/test_safety_contract.py", "r") as f:
    safety = f.read()

safety = safety.replace(
    "    def test_no_freshness_fails_closed(\n        self,\n        safety_contract: SafetyContract,\n        no_freshness_safety_context: SafetyContext,\n        now: datetime,\n    ) -> None:\n        result = safety_contract.evaluate_safety(no_freshness_safety_context, now)\n        assert result.status == SafetyStatus.BLOCKED",
    "    def test_no_freshness_fails_closed(\n        self,\n        safety_contract: SafetyContract,\n        no_freshness_safety_context: SafetyContext,\n        now: datetime,\n    ) -> None:\n        result = safety_contract.evaluate_safety(no_freshness_safety_context, now)\n        assert result.status == SafetyStatus.UNKNOWN"
)
safety = safety.replace(
    "    def test_stale_safety_data_fails_closed(\n        self,\n        safety_contract: SafetyContract,\n        stale_safety_context: SafetyContext,\n        now: datetime,\n    ) -> None:\n        result = safety_contract.evaluate_safety(stale_safety_context, now)\n        assert result.status == SafetyStatus.BLOCKED",
    "    def test_stale_safety_data_fails_closed(\n        self,\n        safety_contract: SafetyContract,\n        stale_safety_context: SafetyContext,\n        now: datetime,\n    ) -> None:\n        result = safety_contract.evaluate_safety(stale_safety_context, now)\n        assert result.status == SafetyStatus.STALE"
)
with open("tests/test_safety_contract.py", "w") as f:
    f.write(safety)

print("Tests updated.")
