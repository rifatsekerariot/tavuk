import pytest
from datetime import datetime, timezone
from database.models import Device
from core.adapters.base import NormalizedReading
from core.adapters.milesight import MilesightAdapter
from core.adapters.chirpstack import ChirpStackAdapter
from core.adapters.registry import adapter_registry

def test_normalized_reading_validation():
    # Valid reading
    r = NormalizedReading(
        zone_id="zone-1",
        device_id="dev-1",
        metric="temperature",
        value=25.0,
        unit="C",
        timestamp=datetime.now(),
        source_vendor="test"
    )
    assert r.quality == "ok"

    # Out of bounds temperature
    r_bad = NormalizedReading(
        zone_id="zone-1",
        device_id="dev-1",
        metric="temperature",
        value=150.0,
        unit="C",
        timestamp=datetime.now(),
        source_vendor="test"
    )
    assert r_bad.quality == "bad_range"

    # Fahrenheit normalization
    r_f = NormalizedReading(
        zone_id="zone-1",
        device_id="dev-1",
        metric="temperature",
        value=77.0,
        unit="F",
        timestamp=datetime.now(),
        source_vendor="test"
    )
    assert r_f.unit == "C"
    assert abs(r_f.value - 25.0) < 0.01
    assert r_f.quality == "ok"


def test_milesight_adapter():
    adapter = MilesightAdapter()
    device = Device(id="UG65_zone-1", zone_id="zone-1", vendor="milesight", codec_id="milesight_direct")
    
    payload = {
        "deviceName": "UG65_zone-1",
        "time": "2026-07-16T14:00:00Z",
        "object": {
            "temperature": 30.5,
            "humidity": 50.0,
            "nh3": 5.0,
            "co2": 600
        }
    }
    
    assert adapter.can_handle("farm/sensors/zone-1", payload) is True
    
    readings = adapter.decode("farm/sensors/zone-1", payload, device)
    assert len(readings) == 4
    
    temp_reading = next(r for r in readings if r.metric == "temperature")
    assert temp_reading.value == 30.5
    assert temp_reading.unit == "C"
    assert temp_reading.zone_id == "zone-1"


def test_chirpstack_adapter():
    adapter = ChirpStackAdapter()
    device = Device(id="CS_001", zone_id="zone-2", vendor="chirpstack", codec_id="chirpstack_generic")
    
    payload = {
        "deviceInfo": {
            "deviceName": "AM307",
            "devEui": "24e124128c012892"
        },
        "time": "2026-07-16T14:00:00Z",
        "object": {
            "temperature": 22.4,
            "humidity": 60.5,
            "co2": 550
        }
    }
    
    assert adapter.can_handle("chirpstack/join", payload) is True
    
    readings = adapter.decode("chirpstack/join", payload, device)
    assert len(readings) == 3
    
    co2_reading = next(r for r in readings if r.metric == "co2")
    assert co2_reading.value == 550.0
    assert co2_reading.unit == "ppm"


def test_registry_resolution():
    payload_milesight = {"deviceName": "UG65_zone-1", "object": {"temperature": 20}}
    payload_chirpstack = {"deviceInfo": {}, "object": {}}
    
    milesight_codec = adapter_registry.resolve_fallback("topic", payload_milesight)
    assert milesight_codec == "milesight_direct"
    
    chirpstack_codec = adapter_registry.resolve_fallback("topic", payload_chirpstack)
    assert chirpstack_codec == "chirpstack_generic"
