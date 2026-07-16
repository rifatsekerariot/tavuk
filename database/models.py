from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.sql import func
from database.config import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(String, primary_key=True, index=True)  # devEUI or unique ID
    zone_id = Column(String, index=True)
    vendor = Column(String)  # e.g. "milesight", "chirpstack"
    model = Column(String)
    protocol = Column(String)  # e.g. "lorawan_chirpstack", "generic_mqtt"
    codec_id = Column(String)  # e.g. "milesight_direct", "chirpstack_generic"
    is_active = Column(Boolean, default=True)

class FarmSettings(Base):
    __tablename__ = 'farm_settings'
    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, default='İzmir')
    lat = Column(Float, default=38.4237)
    lon = Column(Float, default=27.1428)
    house_length = Column(Float, default=100.0)
    house_width = Column(Float, default=14.0)
    ridge_h = Column(Float, default=4.0)
    eaves_h = Column(Float, default=2.5)
    bird_count = Column(Integer, default=30000)
    initial_bird_count = Column(Integer, default=30000)
    reported_mortality = Column(Integer, default=0)
    bird_weight = Column(Float, default=1.8)
    flock_breed = Column(String, default='Ross 308 (Etlik)')
    flock_start_date = Column(DateTime, default=func.now())
    fan_count = Column(Integer, default=10)
    fan_capacity = Column(Float, default=40000.0)
    feed_price = Column(Float, default=15.0)
    meat_price = Column(Float, default=60.0)
    electricity_price = Column(Float, default=3.5)
    mqtt_topic = Column(String, default='farm/sensors')
    sensor_count = Column(Integer, default=6)
    ai_operator_enabled = Column(Boolean, default=True)
    manual_active_fans = Column(Integer, default=2)
    manual_heater_w = Column(Float, default=0.0)
    manual_pad_cooling = Column(Boolean, default=False)
    demo_mode = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class IoTData(Base):
    __tablename__ = 'iot_data'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    zone_id = Column(String, default='zone-1', index=True)
    t_in = Column(Float, nullable=False)
    rh_in = Column(Float, nullable=False)
    nh3_ppm = Column(Float, nullable=True)
    co2_ppm = Column(Float, nullable=True)
    epef_score = Column(Float, nullable=True)
    fcr_penalty = Column(Float, nullable=True)
    mortality_risk = Column(Float, nullable=True)

class AlarmHistory(Base):
    __tablename__ = 'alarm_history'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    type = Column(String, index=True) # danger, warning, critical
    title = Column(String)
    desc = Column(String)
