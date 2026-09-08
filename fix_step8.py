import re

# We will just write a wrapper script to apply ResilienceConfig to MarketProvider etc in context_builder.py
with open("src/confidence/application/context_builder.py", "r") as f:
    content = f.read()

if "from confidence.infrastructure.resilience import ResilienceConfig, execute_with_resilience" not in content:
    content = content.replace(
        "from confidence.domain.models import DecisionContext, InteractionContext, Session\nfrom confidence.domain.ports import MarketProvider, SafetyProvider, SlipProvider",
        "from confidence.domain.models import DecisionContext, InteractionContext, Session\nfrom confidence.domain.ports import MarketProvider, SafetyProvider, SlipProvider\nfrom confidence.infrastructure.resilience import ResilienceConfig, execute_with_resilience"
    )

    # Apply to get_safety_context
    content = content.replace(
        "            safety = await self.safety_provider.get_safety_context(request.session_id, request.anonymous_actor_id)",
        "            safety = await execute_with_resilience(\n                self.safety_provider.get_safety_context,\n                ResilienceConfig(timeout_seconds=0.5, retries=1),\n                request.session_id, request.anonymous_actor_id\n            )"
    )

    # Apply to get_slip_context
    content = content.replace(
        "            slip = await self.slip_provider.get_slip_context(request.slip_id)",
        "            slip = await execute_with_resilience(\n                self.slip_provider.get_slip_context,\n                ResilienceConfig(timeout_seconds=0.5, retries=1),\n                request.slip_id\n            )"
    )
    
    # Apply to get_market_context
    content = content.replace(
        "                market = await self.market_provider.get_market_context(selection.market_id)",
        "                market = await execute_with_resilience(\n                    self.market_provider.get_market_context,\n                    ResilienceConfig(timeout_seconds=0.5, retries=1),\n                    selection.market_id\n                )"
    )

with open("src/confidence/application/context_builder.py", "w") as f:
    f.write(content)

print("Applied to context_builder.py")
