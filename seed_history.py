from database.config import SessionLocal
from database.models import IoTData
from datetime import datetime, timedelta
import random

def seed():
    db = SessionLocal()
    now = datetime.utcnow()
    records = []
    
    for minutes_ago in range(1440, 0, -5):
        ts = now - timedelta(minutes=minutes_ago)
        
        for i in range(1, 7):
            zone_id = f"zone-{i}"
            
            t = 28.0 + random.uniform(-2, 2)
            rh = 60.0 + random.uniform(-5, 5)
            nh3 = 10.0 + random.uniform(-2, 2)
            co2 = 800.0 + random.uniform(-100, 100)
            
            if zone_id == 'zone-3':
                nh3 += 15.0 # Spike
                
            r = IoTData(
                zone_id=zone_id,
                t_in=t,
                rh_in=rh,
                nh3_ppm=nh3,
                co2_ppm=co2,
                timestamp=ts
            )
            records.append(r)
            
    db.add_all(records)
    db.commit()
    print(f"{len(records)} adet gecmis veri eklendi.")

if __name__ == '__main__':
    seed()
