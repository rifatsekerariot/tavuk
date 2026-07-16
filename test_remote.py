import paramiko
import requests
import time
import json
from pprint import pprint

HOST = '185.22.186.132'
USER = 'root'
PASS = 'Qx9#Rz2#Fq8#Dd5!'
PROJECT_DIR = '/var/www/ciftlik'
API_URL = 'https://ciftlik.rifatseker.com.tr/api'

def check_remote_logs():
    print("--- CHECKING REMOTE DOCKER LOGS ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=10)
    
    stdin, stdout, stderr = ssh.exec_command(f"cd {PROJECT_DIR} && docker-compose logs --tail=20")
    logs = stdout.read().decode('utf-8', errors='replace')
    errs = stderr.read().decode('utf-8', errors='replace')
    ssh.close()
    
    if "Error" in logs or "Traceback" in logs or "Exception" in logs:
        print("WARNING: Errors found in docker logs:")
        # Just print lines with error
        for line in logs.split('\n'):
            if "Error" in line or "Traceback" in line or "Exception" in line:
                print(line)
    else:
        print("No obvious Python errors found in the last 20 lines of docker logs.")

def test_api():
    print("\n--- RUNNING API INTEGRATION TESTS ---")
    session = requests.Session()
    
    # Authenticate
    print("Logging in...")
    login_r = session.post(f"{API_URL}/auth/login", json={"username": "admin", "password": "Adana4455*"}, verify=False)
    print("Login status:", login_r.status_code, login_r.json())
    
    # 1. Check if settings endpoint works and has demo_mode
    r = session.get(f"{API_URL}/settings", verify=False)
    settings = r.json()
    print("Initial demo_mode:", settings.get('demo_mode'))
    
    # 2. Reset the DB
    print("Resetting DB...")
    r = session.post(f"{API_URL}/settings/reset", verify=False)
    print("Reset Response:", r.json())
    
    # 3. Check Live Endpoint for waiting status
    print("Checking Live Dashboard immediately after reset...")
    r = session.get(f"{API_URL}/dashboard/live", verify=False)
    live = r.json()
    if isinstance(live, dict) and live.get('status') == 'waiting':
        print("PASS: System is in waiting mode.")
        print("module_down status:", live.get('module_down'))
        if not live.get('module_down'):
            print("PASS: module_down is False, watchdog modal won't show.")
        else:
            print("FAIL: module_down is True!")
    else:
        print("FAIL: Expected waiting status, got:", live)
        
    # 4. Enable Demo Mode
    print("Enabling Demo Mode...")
    r = session.post(f"{API_URL}/settings", json={"demo_mode": True}, verify=False)
    
    # Wait for mock scripts to publish data
    print("Waiting for mock scripts to publish data...")
    data_received = False
    for attempt in range(15):
        print(f"Attempt {attempt + 1}/15: Checking live dashboard...")
        r = session.get(f"{API_URL}/dashboard/live", verify=False)
        live = r.json()
        if isinstance(live, dict) and 'raw' in live:
            print("PASS: Data received from mock sensors!")
            print("Current Temp:", live['raw'].get('t_in'))
            data_received = True
            break
        time.sleep(5)
        
    if not data_received:
        print("FAIL: No data received after enabling demo mode.", live)

if __name__ == '__main__':
    # Suppress insecure request warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    check_remote_logs()
    test_api()
