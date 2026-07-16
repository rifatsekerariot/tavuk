from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
import threading
import httpx
import time
import statistics
from database.config import get_db, engine, Base
from database.models import FarmSettings, IoTData, AlarmHistory, Device, User
from core.mqtt_listener import start_mqtt_listener, virtual_operator_state
from core.biology import calculate_biology_and_finance, calculate_dynamic_weight
import jwt
import bcrypt
import os

from sqlalchemy import text
try:
    with engine.connect() as conn:
        for col, col_type in [
            ("ai_operator_enabled", "BOOLEAN DEFAULT TRUE"),
            ("manual_active_fans", "INTEGER DEFAULT 2"),
            ("manual_heater_w", "FLOAT DEFAULT 0.0"),
            ("manual_pad_cooling", "BOOLEAN DEFAULT FALSE")
        ]:
            try:
                conn.execute(text(f"ALTER TABLE farm_settings ADD COLUMN {col} {col_type};"))
                conn.commit()
            except Exception:
                pass
except Exception:
    pass

Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_jwt(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, "supersecretjwtkey1234!", algorithm="HS256")

def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, "supersecretjwtkey1234!", algorithms=["HS256"])
    except Exception:
        return None

def seed_mock_devices():
    from database.config import SessionLocal
    db = SessionLocal()
    try:
        for i in range(1, 7):
            dev_id = f"UG65_zone-{i}"
            if not db.query(Device).filter(Device.id == dev_id).first():
                dev = Device(
                    id=dev_id,
                    zone_id=f"zone-{i}",
                    vendor="milesight",
                    model="UG65",
                    protocol="generic_mqtt",
                    codec_id="milesight_direct"
                )
                db.add(dev)
        db.commit()
    except Exception as e:
        print(f"Error seeding mock devices: {e}")
    finally:
        db.close()

seed_mock_devices()

def seed_users():
    from database.config import SessionLocal
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin_pwd = os.getenv("ADMIN_PASSWORD", "Adana4455*")
            admin_hash = hash_password(admin_pwd)
            admin_user = User(username="admin", password_hash=admin_hash, role="admin")
            db.add(admin_user)
            
            demo_hash = hash_password("demo123")
            demo_user = User(username="demo", password_hash=demo_hash, role="demo")
            db.add(demo_user)
            db.commit()
    except Exception as e:
        print(f"Error seeding users: {e}")
    finally:
        db.close()

seed_users()

app = FastAPI(title='ARIOT IoT Dashboard')

# In-memory cache for OpenMeteo data
openmeteo_cache = {
    'timestamp': 0,
    'data': None
}

@app.on_event('startup')
def startup_event():
    t = threading.Thread(target=start_mqtt_listener, daemon=True)
    t.start()
    print('MQTT listener thread started.')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.middleware("http")
async def add_cache_control_header(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.mount('/static', StaticFiles(directory='frontend/static'), name='static')


class SettingsUpdate(BaseModel):
    location_name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    house_length: Optional[float] = None
    house_width: Optional[float] = None
    ridge_h: Optional[float] = None
    eaves_h: Optional[float] = None
    bird_count: Optional[int] = None
    initial_bird_count: Optional[int] = None
    reported_mortality: Optional[int] = None
    bird_weight: Optional[float] = None
    flock_breed: Optional[str] = None
    flock_start_date: Optional[datetime] = None
    fan_count: Optional[int] = None
    fan_capacity: Optional[float] = None
    feed_price: Optional[float] = None
    meat_price: Optional[float] = None
    electricity_price: Optional[float] = None
    mqtt_topic: Optional[str] = None
    sensor_count: Optional[int] = None
    ai_operator_enabled: Optional[bool] = None
    manual_active_fans: Optional[int] = None
    manual_heater_w: Optional[float] = None
    manual_pad_cooling: Optional[bool] = None
    demo_mode: Optional[bool] = None


class LoginRequest(BaseModel):
    username: str
    password: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

def get_current_user_from_token(token: str, db: Session) -> Optional[User]:
    payload = decode_jwt(token)
    if not payload:
        return None
    username = payload.get("sub")
    if not username:
        return None
    return db.query(User).filter(User.username == username).first()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = get_current_user_from_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    return user

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin yetkisi gereklidir")
    return current_user

@app.get('/', response_class=HTMLResponse)
def read_root():
    with open('frontend/templates/landing.html', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get('/login', response_class=HTMLResponse)
def read_login(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if token and get_current_user_from_token(token, db):
        return RedirectResponse(url="/demo", status_code=303)
    with open('frontend/templates/login.html', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get('/demo', response_class=HTMLResponse)
def read_demo(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token or not get_current_user_from_token(token, db):
        return RedirectResponse(url="/login", status_code=303)
    with open('frontend/templates/index.html', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get('/manual', response_class=HTMLResponse)
def read_manual(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token or not get_current_user_from_token(token, db):
        return RedirectResponse(url="/login", status_code=303)
    with open('frontend/templates/manual.html', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get('/scada', response_class=HTMLResponse)
def read_scada(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token or not get_current_user_from_token(token, db):
        return RedirectResponse(url="/login", status_code=303)
    with open('frontend/templates/scada.html', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/routes")
def get_routes():
    return [{"path": route.path, "name": route.name} for route in app.routes]

@app.post('/api/auth/login')
def login_endpoint(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Hatalı kullanıcı adı veya şifre")
    token = create_jwt(user.username, user.role)
    response = JSONResponse(content={"status": "ok", "role": user.role, "username": user.username})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax",
        secure=False
    )
    return response

@app.post('/api/auth/logout')
def logout_endpoint():
    response = JSONResponse(content={"status": "ok"})
    response.delete_cookie("access_token")
    return response

@app.post('/api/auth/change-password')
def change_password_endpoint(data: PasswordChangeRequest, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Mevcut şifre hatalı")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Yeni şifre en az 6 karakter olmalıdır")
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"status": "ok", "message": "Şifre başarıyla değiştirildi"}

@app.get('/api/auth/me')
def get_me_endpoint(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}


def get_openmeteo_data(lat, lon):
    global openmeteo_cache
    now = time.time()
    # Cache for 1 hour
    if openmeteo_cache['data'] and (now - openmeteo_cache['timestamp'] < 3600):
        return openmeteo_cache['data']
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,windspeed_10m&forecast_days=14"
        r = httpx.get(url, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        openmeteo_cache['data'] = data
        openmeteo_cache['timestamp'] = now
        return data
    except Exception as e:
        print(f"OpenMeteo fetch error: {e}")
        return None


from fastapi import WebSocket, WebSocketDisconnect
import asyncio

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_ts = None
    try:
        while True:
            from database.config import SessionLocal
            db = SessionLocal()
            try:
                latest = db.query(IoTData).order_by(IoTData.timestamp.desc()).first()
                if latest:
                    if last_ts != latest.timestamp:
                        last_ts = latest.timestamp
                        data = get_live_data(db)
                        await websocket.send_json(data)
            finally:
                db.close()
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass

@app.get('/api/dashboard/live')
def get_live_data(db: Session = Depends(get_db)):
    settings = db.query(FarmSettings).first()
    if not settings:
        settings = FarmSettings()
        db.add(settings)
        db.commit()

    # 1. Fetch latest raw data for UI display (aggregate across zones)
    latest_records = []
    for i in range(1, settings.sensor_count + 1):
        r = db.query(IoTData).filter(IoTData.zone_id == f"zone-{i}").order_by(IoTData.timestamp.desc()).first()
        if r:
            latest_records.append(r)
            
    if not latest_records:
        return {'status': 'waiting', 'message': 'Sensör verisi bekleniyor...', 'module_down': False}

    # Watchdog check: Are sensors dead?
    now_utc = datetime.now(timezone.utc)
    module_down = False
    newest_record = max([r.timestamp for r in latest_records])
    if (now_utc - newest_record).total_seconds() > 120:
        module_down = True
            
    def filter_outliers(data_dict, sensor_type):
        if len(data_dict) < 3:
            return list(data_dict.values()), []
            
        values = list(data_dict.values())
        mean_val = statistics.mean(values)
        stdev_val = statistics.stdev(values) if len(values) > 1 else 0
        
        # Sensorlere ozel minimum kabul edilebilir dogal sapma toleranslari
        tolerances = {
            'Sıcaklık': 3.0,       # 3 dereceye kadar dogal farklilik olabilir
            'Nem': 15.0,           # %15 RH farki normal olabilir
            'Amonyak': 15.0,       # 15 ppm fark normal olabilir
            'Karbondioksit': 300.0 # 300 ppm fark normal olabilir
        }
        min_dev = tolerances.get(sensor_type, 2.0)
        
        filtered_values = []
        outlier_zones = []
        for zone_id, x in data_dict.items():
            # Hem 3 standart sapmadan buyuk olmali HEM DE minimum toleransi asmis olmali
            if abs(x - mean_val) <= max(3 * stdev_val, min_dev):
                filtered_values.append(x)
            else:
                outlier_zones.append(zone_id)
                
        if not filtered_values:
            return values, []
            
        return filtered_values, outlier_zones

    # Build dictionaries for filtering
    t_dict = {r.zone_id: r.t_in for r in latest_records}
    rh_dict = {r.zone_id: r.rh_in for r in latest_records}
    nh3_dict = {r.zone_id: r.nh3_ppm for r in latest_records if r.nh3_ppm is not None}
    co2_dict = {r.zone_id: r.co2_ppm for r in latest_records if r.co2_ppm is not None}

    t_ins, t_outliers = filter_outliers(t_dict, 'Sıcaklık')
    rh_ins, rh_outliers = filter_outliers(rh_dict, 'Nem')
    nh3s, nh3_outliers = filter_outliers(nh3_dict, 'Amonyak')
    co2s, co2_outliers = filter_outliers(co2_dict, 'Karbondioksit')
    
    sensor_faults = []
    for zone in t_outliers: sensor_faults.append(f"{zone} (Sıcaklık)")
    for zone in rh_outliers: sensor_faults.append(f"{zone} (Nem)")
    for zone in nh3_outliers: sensor_faults.append(f"{zone} (Amonyak)")
    for zone in co2_outliers: sensor_faults.append(f"{zone} (CO2)")

    avg_t = sum(t_ins) / len(t_ins) if t_ins else 0.0
    avg_rh = sum(rh_ins) / len(rh_ins) if rh_ins else 0.0
    avg_nh3 = sum(nh3s) / len(nh3s) if nh3s else 0.0
    avg_co2 = sum(co2s) / len(co2s) if co2s else 400.0
    max_nh3 = max(nh3s) if nh3s else 0.0
    max_co2 = max(co2s) if co2s else 400.0
    delta_t = max(t_ins) - min(t_ins) if t_ins else 0.0

    # Find the worst zone for NH3
    worst_nh3_zone = "Belirsiz"
    if nh3s:
        for r in latest_records:
            if r.nh3_ppm == max_nh3:
                worst_nh3_zone = r.zone_id
                break

    # 2. Fetch last 1440 points (approx 24h at 1 point/min per zone? No, history might be huge if 6 zones.)
    # Let's just fetch the last 1440 records overall, which is 1440 / 6 = 240 minutes.
    # To get 24h for 6 zones, we need 6 * 1440 = 8640 records.
    limit_records = settings.sensor_count * 1440
    history = db.query(IoTData).order_by(IoTData.timestamp.desc()).limit(limit_records).all()
    history.reverse() # chronologically
    
    # Simple hour bucketing (grouping 60 * sensor_count points into 1 hour average)
    t_in_hourly = []
    rh_hourly = []
    nh3_hourly = []
    co2_hourly = []
    
    chunk_size = 60 * settings.sensor_count
    for i in range(0, len(history), chunk_size):
        chunk = history[i:i+chunk_size]
        if chunk:
            t_in_hourly.append(sum(c.t_in for c in chunk) / len(chunk))
            rh_hourly.append(sum(c.rh_in for c in chunk if c.rh_in is not None) / len(chunk))
            nh3_hourly.append(sum(c.nh3_ppm for c in chunk if c.nh3_ppm is not None) / len(chunk))
            co2_hourly.append(sum(c.co2_ppm for c in chunk if c.co2_ppm is not None) / len(chunk))
        
    if not t_in_hourly:
        t_in_hourly = [avg_t]
        rh_hourly = [avg_rh]
        nh3_hourly = [max_nh3]
        co2_hourly = [max_co2]

    # 3. Fetch OpenMeteo Current Weather
    weather = get_openmeteo_data(settings.lat, settings.lon)
    current_weather = weather.get('current_weather', {}) if weather else {}
    forecast_hourly = weather.get('hourly', {}) if weather else {}
    
    out_temp = current_weather.get('temperature', '--')
    wind_speed = current_weather.get('windspeed', '--')
    
    out_temp_float = None
    try:
        out_temp_float = float(out_temp)
    except:
        pass

    # 4. Calculate actual biological & financial impact
    # Using the average for timeline, but the real time is max.
    # Calculate dynamic age
    now_naive = datetime.utcnow()
    bird_age_days = (now_naive - settings.flock_start_date).total_seconds() / 86400.0 if settings.flock_start_date else 0.0
    
    updated_at_naive = settings.updated_at.replace(tzinfo=None) if settings.updated_at else now_naive
    age_days_at_record = (updated_at_naive - settings.flock_start_date).total_seconds() / 86400.0 if settings.flock_start_date else 0.0

    dynamic_weight = calculate_dynamic_weight(
        recorded_weight=settings.bird_weight, 
        current_age_days=bird_age_days, 
        breed=settings.flock_breed,
        age_days_at_record=0.0
    )

    # 4.5 Get actual fan state
    active_fans = None
    if virtual_operator_state and 'active_fans' in virtual_operator_state:
        active_fans = virtual_operator_state['active_fans']

    # Append the instantaneous live values so the AI decision engine reacts immediately
    if avg_t > 0:
        t_in_hourly.append(avg_t)
        rh_hourly.append(avg_rh)
        nh3_hourly.append(avg_nh3)
        co2_hourly.append(avg_co2)

    bio_results = calculate_biology_and_finance(
        t_in_array=t_in_hourly,
        rh_out_array=[],
        nh3_array=nh3_hourly,
        co2_array=co2_hourly,
        fan_count=settings.fan_count,
        fan_capacity=settings.fan_capacity,
        width=settings.house_width,
        ridge_h=settings.ridge_h,
        eaves_h=settings.eaves_h,
        bird_count=settings.bird_count,
        initial_bird_count=settings.initial_bird_count,
        reported_mortality=settings.reported_mortality,
        bird_weight=dynamic_weight,
        bird_age=bird_age_days,
        kwh_consumed=1.5,
        feed_price=settings.feed_price,
        meat_price=settings.meat_price,
        electricity_price=settings.electricity_price,
        delta_t=delta_t,
        worst_nh3_zone=worst_nh3_zone,
        t_out=out_temp_float,
        breed=settings.flock_breed,
        forecast_hourly=forecast_hourly,
        current_active_fans=active_fans
    )
    
    # Add spatial variance data to bio_results
    bio_results['delta_t'] = round(delta_t, 2)
    bio_results['worst_nh3_zone'] = worst_nh3_zone
    bio_results['current_weight'] = round(dynamic_weight, 3)
    bio_results['age_days'] = bio_results.get('bird_age_days', 0)

    # Add Sensor Fault Alarms
    if 'actions' not in bio_results:
        bio_results['actions'] = []
        
    if sensor_faults:
        fault_str = ", ".join(sensor_faults)
        bio_results['actions'].insert(0, {
            'type': 'danger',
            'title': 'Sensör Uyarısı!',
            'desc': f"{fault_str} sensöründen hatalı veri geliyor. Lütfen cihazın kablosunu ve temizliğini kontrol edin. Geçici olarak bu cihazın verisi dikkate alınmıyor."
        })

    # Add Actuator Diagnostic Alarm
    if virtual_operator_state and virtual_operator_state.get('diagnostic_alarm'):
        bio_results['actions'].insert(0, {
            'type': 'critical',
            'title': 'SİSTEM DONANIM ARIZASI',
            'desc': virtual_operator_state['diagnostic_alarm']
        })

    # Save alarms to history
    for action in bio_results.get('actions', []):
        atype = action.get('type')
        if atype in ['warning', 'danger', 'critical']:
            title = action.get('title')
            # Check if same alarm title was logged in the last 30 mins
            thirty_mins_ago = now_utc - timedelta(minutes=30)
            recent_alarm = db.query(AlarmHistory).filter(
                AlarmHistory.title == title,
                AlarmHistory.timestamp >= thirty_mins_ago
            ).first()
            if not recent_alarm:
                new_alarm = AlarmHistory(
                    type=atype,
                    title=title,
                    desc=action.get('desc')
                )
                db.add(new_alarm)
                db.commit()

    return {
        'timestamp': str(latest_records[0].timestamp),
        'raw': {
            't_in': round(avg_t, 1),
            'rh_in': round(avg_rh, 1),
            'nh3': round(avg_nh3, 1), # Use average for display
            'co2': round(avg_co2, 0), # Use average for display
            'zones': [{'zone': r.zone_id, 't_in': r.t_in, 'rh_in': r.rh_in, 'nh3': r.nh3_ppm, 'co2': r.co2_ppm} for r in latest_records]
        },
        'module_down': module_down,
        'openmeteo': {
            't_out': out_temp,
            'wind_speed': wind_speed,
            'location': settings.location_name
        },
        'bio': bio_results,
        'actuators': virtual_operator_state
    }


@app.get('/api/dashboard/history')
def get_history(range: Optional[str] = "1h", db: Session = Depends(get_db)):
    now = datetime.utcnow()
    
    if range == "1h":
        start_time = now - timedelta(hours=1)
        bucket_size = 60 # 1 minute
    elif range == "24h":
        start_time = now - timedelta(hours=24)
        bucket_size = 1800 # 30 mins
    elif range == "7d":
        start_time = now - timedelta(days=7)
        bucket_size = 14400 # 4 hours
    elif range == "30d":
        start_time = now - timedelta(days=30)
        bucket_size = 86400 # 1 day
    else: # all
        start_time = datetime.min
        bucket_size = 86400 * 7 # 1 week
        
    query = db.query(IoTData)
    if start_time != datetime.min:
        query = query.filter(IoTData.timestamp >= start_time)
        
    records = query.order_by(IoTData.timestamp.asc()).all()
    
    if not records:
        return []
        
    # Agregate data
    first_time = records[0].timestamp
    buckets = {}
    
    for r in records:
        delta_sec = (r.timestamp - first_time).total_seconds()
        b_idx = int(delta_sec // bucket_size)
        if b_idx not in buckets:
            buckets[b_idx] = []
        buckets[b_idx].append(r)
        
    result = []
    for b_idx in sorted(buckets.keys()):
        chunk = buckets[b_idx]
        # Use the average timestamp of the chunk
        avg_ts = sum(c.timestamp.timestamp() for c in chunk) / len(chunk)
        dt = datetime.fromtimestamp(avg_ts)
        
        if range in ["1h", "24h"]:
            t_label = dt.strftime('%H:%M')
        else:
            t_label = dt.strftime('%d %b %H:%M')
            
        t_in_avg = sum(c.t_in for c in chunk) / len(chunk)
        rh_in_avg = sum(c.rh_in for c in chunk) / len(chunk)
        
        nh3s = [c.nh3_ppm for c in chunk if c.nh3_ppm is not None]
        co2s = [c.co2_ppm for c in chunk if c.co2_ppm is not None]
        
        nh3_avg = sum(nh3s) / len(nh3s) if nh3s else 0
        co2_avg = sum(co2s) / len(co2s) if co2s else 0
        
        result.append({
            'time': t_label,
            't_in': round(t_in_avg, 2),
            'rh_in': round(rh_in_avg, 2),
            'nh3': round(nh3_avg, 2),
            'co2': round(co2_avg, 2)
        })
        
    return result


@app.get('/api/dashboard/alarms')
def get_alarms(db: Session = Depends(get_db)):
    alarms = db.query(AlarmHistory).order_by(AlarmHistory.timestamp.desc()).limit(50).all()
    result = []
    for a in alarms:
        result.append({
            'timestamp': a.timestamp.strftime('%Y-%m-%d %H:%M'),
            'type': a.type,
            'title': a.title,
            'desc': a.desc
        })
    return result


@app.get('/api/settings')
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(FarmSettings).first()
    if not settings:
        settings = FarmSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return {
        'location_name': settings.location_name,
        'lat': settings.lat,
        'lon': settings.lon,
        'house_length': settings.house_length,
        'house_width': settings.house_width,
        'ridge_h': settings.ridge_h,
        'eaves_h': settings.eaves_h,
        'bird_count': settings.bird_count,
        'initial_bird_count': settings.initial_bird_count,
        'reported_mortality': settings.reported_mortality,
        'bird_weight': settings.bird_weight,
        'flock_breed': settings.flock_breed,
        'flock_start_date': settings.flock_start_date.isoformat() if settings.flock_start_date else None,
        'fan_count': settings.fan_count,
        'fan_capacity': settings.fan_capacity,
        'feed_price': settings.feed_price,
        'meat_price': settings.meat_price,
        'electricity_price': settings.electricity_price,
        'mqtt_topic': settings.mqtt_topic,
        'sensor_count': settings.sensor_count,
        'ai_operator_enabled': settings.ai_operator_enabled,
        'manual_active_fans': settings.manual_active_fans,
        'manual_heater_w': settings.manual_heater_w,
        'manual_pad_cooling': settings.manual_pad_cooling,
        'demo_mode': settings.demo_mode,
    }


@app.post('/api/settings')
def update_settings(data: SettingsUpdate, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    settings = db.query(FarmSettings).first()
    if not settings:
        settings = FarmSettings()
        db.add(settings)

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)

    # Invalidate openmeteo cache if location changed
    if 'lat' in update_data or 'lon' in update_data:
        global openmeteo_cache
        openmeteo_cache['data'] = None
        openmeteo_cache['timestamp'] = 0

    db.commit()
    db.refresh(settings)
    return {'status': 'ok', 'message': 'Ayarlar kaydedildi.'}

class MortalityReport(BaseModel):
    dead_birds: int

@app.post('/api/mortality/report')
def report_mortality(data: MortalityReport, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    settings = db.query(FarmSettings).first()
    if not settings:
        return {'status': 'error', 'message': 'Ayarlar bulunamadı.'}
    
    if data.dead_birds > 0:
        settings.reported_mortality += data.dead_birds
        settings.bird_count = max(0, settings.bird_count - data.dead_birds)
        db.commit()
        db.refresh(settings)
        
    return {
        'status': 'ok', 
        'message': f'{data.dead_birds} fire başarıyla kaydedildi.',
        'new_bird_count': settings.bird_count,
        'total_mortality': settings.reported_mortality
    }

@app.post('/api/settings/reset')
def reset_mock_data(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    try:
        from database.models import IoTData, AlarmHistory, FarmSettings
        db.query(IoTData).delete()
        db.query(AlarmHistory).delete()
        
        settings = db.query(FarmSettings).first()
        if settings:
            settings.reported_mortality = 0
            settings.bird_count = settings.initial_bird_count
            
        db.commit()
        return {'status': 'ok', 'message': 'Geçmiş veriler, alarmlar ve fire (ölüm) kayıtları başarıyla sıfırlandı.'}
    except Exception as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}
