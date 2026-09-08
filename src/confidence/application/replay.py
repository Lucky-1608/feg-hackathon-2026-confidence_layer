"""Event replay mechanism."""


class ReplayManager:
    """Replays events from Kafka into the decision engine."""

    def __init__(self) -> None:
        self.replaying = False

    def start_replay(self, start_offset: int) -> None:
        self.replaying = True
        # In real app, spawn background task to seek and consume

    def stop_replay(self) -> None:
        self.replaying = False
