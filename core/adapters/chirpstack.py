from datetime import datetime, timezone
from core.adapters.base import SensorAdapter, NormalizedReading
from database.models import Device

class ChirpStackAdapter(SensorAdapter):
    def can_handle(self, topic: str, payload: dict) -> bool:
        # ChirpStack MQTT payloads usually contain "deviceInfo" or "deduplicationId" or "devEui"
        if "deviceInfo" in payload or "devEui" in payload:
            return True
        return False

    def decode(self, topic: str, payload: dict, device: Device) -> list[NormalizedReading]:
        obj = payload.get("object", {})
        
        ts_str = payload.get("time")
        if ts_str:
            try:
                clean_ts = ts_str.replace("Z", "+00:00")
                ts = datetime.fromisoformat(clean_ts)
            except Exception:
                ts = datetime.now(timezone.utc)
        else:
            ts = datetime.now(timezone.utc)

        readings = []
        metrics_mapping = {
            "temperature": "temperature",
            "humidity": "humidity",
            "nh3": "nh3",
            "co2": "co2"
        }
        
        units = {
            "temperature": "C",
            "humidity": "%",
            "nh3": "ppm",
            "co2": "ppm"
        }

        for raw_key, norm_metric in metrics_mapping.items():
            if raw_key in obj and obj[raw_key] is not None:
                readings.append(NormalizedReading(
                    zone_id=device.zone_id,
                    device_id=device.id,
                    metric=norm_metric,
                    value=float(obj[raw_key]),
                    unit=units[norm_metric],
                    timestamp=ts,
                    source_vendor=device.vendor or "chirpstack"
                ))

        return readings
