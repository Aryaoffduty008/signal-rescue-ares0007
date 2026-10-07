class Mission:

    def __init__(
        self,
        mission_id,
        title,
        briefing,
        objective,
        hint,
        validator
    ):

        self.mission_id = mission_id
        self.title = title
        self.briefing = briefing
        self.objective = objective
        self.hint = hint
        self.validator = validator

    def display(self):

        print()
        print("==============================================")
        print(f"        🛰️ ARES-7 — MISSION {self.mission_id}")
        print(f"             {self.title}")
        print("==============================================")

        print()
        print("MISSION BRIEFING")
        print("----------------------------------------------")
        print(self.briefing)

        print()
        print("MISSION OBJECTIVE")
        print("----------------------------------------------")
        print(self.objective)

    def check_answer(self, answer):

        return self.validator(answer)