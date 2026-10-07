class GameState:

    def __init__(self):

        self.current_mission = 1

        self.total_score = 0

        self.signal_integrity = 100

        self.missions_completed = 0

        self.hints_used = 0

        self.attempts = 0

        self.completed_missions = set()

        self.unlocked_missions = {
            1
        }

    # =================================================
    # MISSION
    # =================================================

    def start_mission(
        self,
        mission_id
    ):

        self.current_mission = mission_id

    def complete_mission(
        self,
        mission_id,
        score
    ):

        if mission_id not in self.completed_missions:

            self.completed_missions.add(
                mission_id
            )

            self.missions_completed += 1

        self.total_score += score

        next_mission = (
            mission_id + 1
        )

        self.unlocked_missions.add(
            next_mission
        )

    # =================================================
    # ATTEMPTS
    # =================================================

    def record_attempt(self):

        self.attempts += 1

    # =================================================
    # HINTS
    # =================================================

    def use_hint(self):

        self.hints_used += 1

        self.signal_integrity = max(
            0,
            self.signal_integrity - 5
        )

    # =================================================
    # WRONG ANSWER
    # =================================================

    def wrong_attempt(self):

        self.signal_integrity = max(
            0,
            self.signal_integrity - 10
        )

    # =================================================
    # STATUS
    # =================================================

    def get_status(self):

        return {
            "mission": self.current_mission,
            "score": self.total_score,
            "integrity": self.signal_integrity,
            "completed": len(
                self.completed_missions
            ),
            "hints": self.hints_used,
            "attempts": self.attempts,
        }

    # =================================================
    # RESET
    # =================================================

    def reset(self):

        self.current_mission = 1

        self.total_score = 0

        self.signal_integrity = 100

        self.missions_completed = 0

        self.hints_used = 0

        self.attempts = 0

        self.completed_missions = set()

        self.unlocked_missions = {
            1
        }