from locust import HttpUser, between, task


class ConfidenceUser(HttpUser):
    wait_time = between(0.1, 1.0)

    @task
    def decide(self):
        self.client.post(
            "/v1/decisions",
            json={
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
                    "interaction_velocity": 3.0,
                },
            },
            headers={"Authorization": "Bearer demo-token"},
        )
