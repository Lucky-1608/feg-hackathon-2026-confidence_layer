"""Adversarial & Edge Case Tests."""

from confidence.domain.models import InteractionContext


def test_extreme_interaction_velocity() -> None:
    # E.g. interaction_velocity = 9999.9
    ctx = InteractionContext(interaction_velocity=9999.9)
    assert ctx.interaction_velocity == 9999.9
