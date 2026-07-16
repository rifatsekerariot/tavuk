from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from database.models import Device

class NormalizedReading(BaseModel):
    zone_id: str
    device_id: str
    metric: str  # "temperature", "humidity", "nh3", "co2"
    value: float
    unit: str  # "C", "%", "ppm"
    timestamp: datetime
    source_vendor: str
    quality: str = "ok"

    @model_validator(mode="after")
    def validate_and_normalize(self) -> 'NormalizedReading':
        # Unit normalization (e.g., Fahrenheit to Celsius)
        if self.metric == "temperature" and self.unit.upper() == "F":
            self.value = (self.value - 32) * 5 / 9
            self.unit = "C"
        
        # Range validations & quality flagging
        if self.metric == "temperature" and not (-40 <= self.value <= 80):
            self.quality = "bad_range"
        elif self.metric == "humidity" and not (0 <= self.value <= 100):
            self.quality = "bad_range"
        elif self.metric == "nh3" and self.value < 0:
            self.quality = "bad_range"
        elif self.metric == "co2" and self.value < 0:
            self.quality = "bad_range"
            
        return self

class SensorAdapter(ABC):
    @abstractmethod
    def can_handle(self, topic: str, payload: dict) -> bool:
        pass

    @abstractmethod
    def decode(self, topic: str, payload: dict, device: Device) -> list[NormalizedReading]:
        pass
