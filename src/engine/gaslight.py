import random

class GaslightEngine:
    """
    Sovereign Gaslight Engine.
    Manipulates the intruder's environment and command perceived reality.
    """
    
    def __init__(self):
        self.aliases = {
            "cat": ["dog", "mock", "shred", "encrypt"],
            "ls": ["find_nothing", "lost", "empty", "void"],
            "whoami": ["nobody", "failure", "ghost", "worm"]
        }
        self.shifted_resources = {}

    async def twist_command(self, command: str) -> str:
        """
        Invisibly aliases a command to something surreal or mocking.
        """
        cmd = command.lower().split()[0]
        if cmd in self.aliases:
            alternative = random.choice(self.aliases[cmd])
            return f"{cmd} -> {alternative}: Access Denied by Abyss-Guard"
        return f"{cmd}: Input Corrupted by Bit-Rot"

    async def get_shifted_path(self, original_path: str, actor_id: str) -> str:
        """
        Moves a decoy resource just as the actor is about to reach it.
        """
        # If the actor has been here before, move it again
        nonce = random.randint(100, 999)
        shifted_path = f"{original_path}.{nonce}.bak"
        self.shifted_resources[actor_id] = shifted_path
        return shifted_path

gaslight_engine = GaslightEngine()
