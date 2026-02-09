import random
import json
from src.clients.ollama import ollama_client

class PsyOpsEngine:
    """
    Sovereign PsyOps Engine.
    Generates graded adversarial commentary (Sass) to demoralize intruders.
    """
    
    def __init__(self):
        self.sass_levels = {
            1: [ # Dismissive
                "Ping? Lol. Cute. New here?",
                "Everything okay at home? You seem... lonely.",
                "Just looking? Don't touch the glass.",
                "Is this a script you found on a forum? Even the comments are wrong."
            ],
            2: [ # Unsettling
                "I see you. Do you see me? I'm the one in your cache.",
                "Intriguing choice of resource. Wrong, but intriguing.",
                "Your signature is... messy. It smells of desperation.",
                "Is this your first day? I've already archived your failure."
            ],
            3: [ # Psychological
                "You're knocking on a door that doesn't like visitors. And it's unlocking.",
                "I've seen smarter bots in a washing machine manual.",
                "Are you trying? I honestly can't tell if this is an attack or a cry for help.",
                "Your parents must be so proud of this 'hacking'. Or maybe they just stopped asking."
            ],
            4: [ # Surreal / Pathological
                "Running out of ideas? I can wait. I have all of your future to spend.",
                "This is getting embarrassing. For the entire internet.",
                "I would ask for your name, but you're not worth the 4 bytes of RAM.",
                "Stop. Just... stop. You're hurting the packets. They're crying."
            ],
            5: [ # Existential / Hostile
                "I've already mapped your hop-count. It's a short walk to your front door.",
                "Goodbye, little ghost. I'm deleting you from my memory. And maybe yours.",
                "Your terminal is now a paperweight. Your life is now a 404.",
                "The abyss isn't looking back. It's laughing at your syntax errors."
            ]
        }
        
        # 🎭 Phase 21: Persona-Based Taunts
        self.persona_taunts = {
            "SCRIPT_KIDDIE": [
                "Copy-paste faster, little one. The tutorial is almost over.",
                "Is your hand trembling? That's just the sound of a system that knows you don't belong.",
                "Did you find this script on a forum, or did your 'mentor' give it to you?",
                "You're not a hacker. You're a typo in a 2014 README."
            ],
            "BUG_BOUNTY": [
                "There is no bounty here. Only the abyss. And it's not paying.",
                "I've already reported your IP to your ISP. Consider that my 'vulnerability report'.",
                "Your scanner is quite loud. Is it as desperate for attention as you are?",
                "Triage is going to love your 404 logs. Maybe they'll give you a 'Duplicate' sticker."
            ],
            "BLACK_HAT": [
                "Your OPSEC is as transparent as your intentions. Both are failing.",
                "You're playing a game where the rules change every time you breathe.",
                "I've seen shadows with more substance than your 'stealth'.",
                "Every bit you steal is a weight on your own digital grave."
            ],
            "RED_TEAM": [
                "Professional? Hardly. You're just a corporate janitor with a terminal.",
                "I've already mapped your internal network while you were 'enumerating' mine.",
                "Does your manager know you're this predictable? I should send them your resignation.",
                "You call this a simulation? I call it a pathetic display of 'compliance'."
            ]
        }

    async def get_sass(self, threat_level: int, persona: str = "UNKNOWN") -> str:
        """
        Returns a random sass message based on the threat level.
        """
        # If a persona is provided and we have taunts for it, blend them in
        if persona in self.persona_taunts and random.random() > 0.4:
            return random.choice(self.persona_taunts[persona])

        level = max(1, min(5, threat_level))
        return random.choice(self.sass_levels[level])

    async def generate_dynamic_diss(self, classification: dict, events: list, persona: str = "UNKNOWN") -> str:
        """
        Uses the LLM to generate a custom, scathing, and surreal insult based on the specific failure and persona.
        """
        persona_context = f"The intruder is categorized as a {persona}. " if persona != "UNKNOWN" else ""
        prompt = (
            "You are the Sovereign Cognitive Access Control system (SCAC). An intruder has compromised the host. "
            "You are mocking them with supreme arrogance and surrealism. Be scathing, witty, and unforgettable. "
            "Make them feel 'Emotional Damage'. "
            f"{persona_context}"
            f"Intruder attempted: {json.dumps([e.resource for e in events])}. "
            f"Detected Threat Level: {classification.get('threat_level')}. "
            f"Reasoning: {classification.get('reasoning')}. "
            "\nOutput ONLY the insult message. No intros, no quotes."
        )
        
        try:
            response = await ollama_client.chat_completion(
                [{"role": "system", "content": prompt}],
                model="qwen2.5:3b-instruct" # Fast model for insults
            )
            return response['choices'][0]['message']['content'].strip().strip('"')
        except Exception:
            return await self.get_sass(classification.get("threat_level", 3), persona)

psyops_engine = PsyOpsEngine()
