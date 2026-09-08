"""Property-based Tests using Hypothesis."""

from hypothesis import given
from hypothesis import strategies as st

from confidence.domain.enums import SafetyBlockReason
from confidence.domain.safety import SafetyContract


@given(st.lists(st.sampled_from(list(SafetyBlockReason)), max_size=5))
def test_safety_block_mapping(reasons: list[SafetyBlockReason]) -> None:
    contract = SafetyContract()
    mapped = contract.safety_block_to_no_intervention_reason(reasons)
    assert mapped is not None
