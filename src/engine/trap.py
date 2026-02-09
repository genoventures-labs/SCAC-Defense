class TrapEngine:
    """
    Sovereign Trap Engine.
    Generates persona-specific ASCII art for the 'Final Fate' experience.
    """
    
    def __init__(self):
        self.traps = {
            "SCRIPT_KIDDIE": """
    +---------------------------------------+
    |  [ ERROR: TUTORIAL EXPIRED ]          |
    |                                       |
    |      (o)   (o)   (o)   (o)   (o)      |
    |       |     |     |     |     |       |
    |    [ CAGE ] [ CAGE ] [ CAGE ] [ CAGE ]|
    |                                       |
    |  PLEASE REINSTALL WINDOWS TO CONTINUE |
    +---------------------------------------+
""",
            "BUG_BOUNTY": """
    _________________________________________
   /                                         \\
  |  [ STATUS: DUPLICATE / N/A / CLOSED ]    |
  |                                          |
  |      .---------------------------.       |
  |     /    TRIAGE VOID (NO PAY)     \\      |
  |    |  [ ] [ ] [ ] [ ] [ ] [ ] [ ]  |     |
  |     \\_____________________________/      |
  |                                          |
   \\_________________________________________/
""",
            "BLACK_HAT": """
     ___________________________________
    /                                   \\
   |   [ ALERT: FEDERATED TRAP ACTIVE ]  |
   |                                     |
   |       _______         _______       |
   |      |       |       |       |      |
   |    --| [X.X] |--   --| [X.X] |--    |
   |      |_______|       |_______|      |
   |                                     |
   |   YOUR OPSEC IS NOW PROPERTY OF SCAC|
    \\___________________________________/
""",
            "RED_TEAM": """
    +---------------------------------------+
    | [ REPORT GEN: CRITICAL FAILURE ]      |
    |                                       |
    |    DEAR MANAGER,                      |
    |    I GOT STUCK IN A MIRROR-WORLD.     |
    |    PLEASE SEND A NEW TEAM.            |
    |                                       |
    |    [ CORPORATE SLA BREACHED ]         |
    +---------------------------------------+
""",
            "UNKNOWN": """
    =========================================
    |          THE SOVEREIGN ABYSS          |
    |                                       |
    |          YOU ARE NOW STUCK.           |
    |                                       |
    =========================================
"""
        }

    async def get_final_fate(self, persona: str) -> str:
        """
        Returns the ASCII trap for the given persona.
        """
        return self.traps.get(persona, self.traps["UNKNOWN"])

trap_engine = TrapEngine()
