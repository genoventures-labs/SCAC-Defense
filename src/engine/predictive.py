from src.clients.pocketbase import pb_client
import math

class PredictiveEngine:
    """
    Sovereign Predictive Engine.
    Analyzes historical risk trends to anticipate future adversarial shifts.
    """
    
    async def calculate_risk_velocity(self, actor_id: str) -> float:
        """
        Calculates the velocity of threat level changes for an actor.
        Velocity > 0 means the actor is becoming more dangerous.
        """
        try:
            # 1. Fetch last 5 trajectories for this actor
            trajectories = pb_client.get_collection("scac_trajectories").get_full_list(
                5, {'filter': f'actor_id = "{actor_id}"', 'sort': '-created'}
            )
            
            if len(trajectories) < 2:
                return 0.0 # Not enough data for velocity
                
            # 2. Extract threat levels (1-5)
            # In a real system, we'd join with classifications, 
            # for now we'll simulate based on counts or status
            levels = []
            for t in trajectories:
                # [Simulation] High threat if locked or had many logs
                level = 1.0
                if getattr(t, 'classification_status', '') == 'ADVERSARIAL':
                    level = 5.0
                elif getattr(t, 'classification_status', '') == 'SUSPICIOUS':
                    level = 3.0
                levels.append(level)
                
            # 3. Simple Gradient Calculation (Current - Previous)
            # We reverse to get chronological order [oldest -> newest]
            levels.reverse()
            total_change = sum(levels[i] - levels[i-1] for i in range(1, len(levels)))
            velocity = total_change / (len(levels) - 1)
            
            return round(velocity, 2)
            
        except Exception as e:
            print(f"⚠️ Predictive Analytics Failed for {actor_id}: {str(e)}")
            return 0.0

    async def get_prediction(self, actor_id: str) -> dict:
        """
        Generates a behavioral prediction based on velocity and state.
        """
        velocity = await self.calculate_risk_velocity(actor_id)
        
        prediction = {
            "risk_velocity": velocity,
            "trend": "STABLE" if velocity == 0 else ("ESCALATING" if velocity > 0 else "DE-ESCALATING"),
            "probability_of_breach": min(1.0, max(0.0, 0.1 + (velocity * 0.5)))
        }
        
        return prediction

predictive_engine = PredictiveEngine()
