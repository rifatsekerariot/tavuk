from core.adapters.base import SensorAdapter
from core.adapters.milesight import MilesightAdapter
from core.adapters.chirpstack import ChirpStackAdapter

class AdapterRegistry:
    def __init__(self):
        self._adapters: dict[str, SensorAdapter] = {}
        # Pre-register supported adapters
        self.register("milesight_direct", MilesightAdapter())
        self.register("chirpstack_generic", ChirpStackAdapter())

    def register(self, codec_id: str, adapter: SensorAdapter):
        self._adapters[codec_id] = adapter

    def get_by_codec(self, codec_id: str) -> SensorAdapter | None:
        return self._adapters.get(codec_id)

    def resolve_fallback(self, topic: str, payload: dict) -> str | None:
        for codec_id, adapter in self._adapters.items():
            if adapter.can_handle(topic, payload):
                return codec_id
        return None

# Global registry instance
adapter_registry = AdapterRegistry()
