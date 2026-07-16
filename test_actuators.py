import httpx

try:
    r = httpx.get('https://ciftlik.rifatseker.com.tr/api/dashboard/live', timeout=10.0)
    print("API Response:", r.status_code)
    data = r.json()
    actions = data.get('biology', {}).get('actions', [])
    for a in actions:
        print("-", a.get('title'))
except Exception as e:
    print("Error:", e)
