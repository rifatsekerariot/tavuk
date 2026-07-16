from datetime import datetime, timezone
from core.adapters.base import SensorAdapter, NormalizedReading
from database.models import Device

class MilesightAdapter(SensorAdapter):
    def can_handle(self, topic: str, payload: dict) -> bool:
        # Fallback heuristic: check if deviceName starts with UG65 or payload has 'object' containing Milesight metrics
        device_name = payload.get("deviceName", "")
        if device_name.startswith("UG65"):
            return True
        obj = payload.get("object", {})
        if "temperature" in obj and "humidity" in obj and ("nh3" in obj or "co2" in obj):
            return True
        return False

    def decode(self, topic: str, payload: dict, device: Device) -> list[NormalizedReading]:
        obj = payload.get("object", payload)
        
        # Determine timestamp
        ts_str = payload.get("time")
        if ts_str:
            try:
                # Parse standard ISO string, handling Z/offset
                clean_ts = ts_str.replace("Z", "+00:00")
                ts = datetime.fromisoformat(clean_ts)
            except Exception:
                ts = datetime.now(timezone.utc)
        else:
            ts = datetime.now(timezone.utc)

        readings = []
        metrics_mapping = {
            "temperature": "temperature",
            "t_in": "temperature",
            "humidity": "humidity",
            "rh_in": "humidity",
            "nh3": "nh3",
            "nh3_ppm": "nh3",
            "co2": "co2",
            "co2_ppm": "co2"
        }

        # Units mapping
        units = {
            "temperature": "C",
            "humidity": "%",
            "nh3": "ppm",
            "co2": "ppm"
        }

        for raw_key, norm_metric in metrics_mapping.items():
            if raw_key in obj and obj[raw_key] is not None:
                # Add to readings if not already added under normalized name
                if not any(r.metric == norm_metric for r in readings):
                    readings.append(NormalizedReading(
                        zone_id=device.zone_id,
                        device_id=device.id,
                        metric=norm_metric,
                        value=float(obj[raw_key]),
                        unit=units[norm_metric],
                        timestamp=ts,
                        source_vendor=device.vendor or "milesight"
                    ))

        return readings
