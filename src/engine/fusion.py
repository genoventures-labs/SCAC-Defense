import os
import psutil
from datetime import datetime

class FusionEngine:
    """
    Sovereign Fusion Engine.
    Collects and normalizes system-level telemetry logs for reasoning context.
    """
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())

    async def get_system_telemetry(self) -> dict:
        """
        Captures a snapshot of host-level metrics.
        """
        try:
            load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
            cpu_pct = psutil.cpu_percent(interval=None)
            mem_pct = psutil.virtual_memory().percent
            
            # Application-specific metrics
            app_cpu = self.process.cpu_percent()
            app_mem = self.process.memory_info().rss / (1024 * 1024) # MB
            
            return {
                "host_load": load,
                "host_cpu_usage": cpu_pct,
                "host_mem_usage": mem_pct,
                "app_cpu_usage": app_cpu,
                "app_memory_mb": app_mem,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"⚠️ Fusion Telemetry Failed: {str(e)}")
            return {"status": "telemetry_unavailable"}

    async def detect_anomaly(self, telemetry: dict) -> float:
        """
        Detects system-level anomalies (spikes/threshold violations).
        Returns a score between 0.0 and 1.0.
        """
        if "telemetry_unavailable" in telemetry.values():
            return 0.0
            
        score = 0.0
        
        # High Host Load
        if telemetry.get("host_load", 0) > 4.0:
            score += 0.4
            
        # High CPU Spike
        if telemetry.get("host_cpu_usage", 0) > 85.0:
            score += 0.3
            
        # High Memory Pressure
        if telemetry.get("host_mem_usage", 0) > 90.0:
            score += 0.2
            
        return min(1.0, score)

fusion_engine = FusionEngine()
