import httpx
try:
    r = httpx.get('https://ciftlik.rifatseker.com.tr/api/dashboard/live', timeout=10.0)
    print(r.json())
except Exception as e:
    print("Error:", e)
