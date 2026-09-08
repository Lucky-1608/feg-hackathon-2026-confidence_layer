import asyncio
from httpx import AsyncClient, ASGITransport
from confidence.api.app import app

async def test():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/v1/decisions", headers={"Authorization": "Bearer demo-token"}, json={
            "session_id": "00000000-0000-0000-0000-000000000000",
            "anonymous_actor_id": "actor-001",
            "client_version": "1.0",
            "slip_id": "slip-001",
            "interaction": {
                "session_age_seconds": 120.0,
                "recent_backtracks": 1,
                "dwell_time_seconds": 15.0,
                "selection_changes": 0,
                "stake_changes": 0,
                "odds_changed": True,
                "time_since_slip_creation_seconds": 60.0,
                "confirmation_attempts": 2,
                "interaction_velocity": 3.0
            }
        })
        print(response.status_code)
        print(response.json())

asyncio.run(test())
