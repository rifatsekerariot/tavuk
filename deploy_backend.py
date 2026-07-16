import paramiko
import os

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print(f"Creating directory {project_dir}/core/adapters on remote server...")
ssh.exec_command(f"mkdir -p {project_dir}/core/adapters")

sftp = ssh.open_sftp()

files_to_upload = [
    ("d:/Antigravity/tavuk/core/biology.py", f"{project_dir}/core/biology.py"),
    ("d:/Antigravity/tavuk/core/mqtt_listener.py", f"{project_dir}/core/mqtt_listener.py"),
    ("d:/Antigravity/tavuk/core/adapters/__init__.py", f"{project_dir}/core/adapters/__init__.py"),
    ("d:/Antigravity/tavuk/core/adapters/base.py", f"{project_dir}/core/adapters/base.py"),
    ("d:/Antigravity/tavuk/core/adapters/milesight.py", f"{project_dir}/core/adapters/milesight.py"),
    ("d:/Antigravity/tavuk/core/adapters/chirpstack.py", f"{project_dir}/core/adapters/chirpstack.py"),
    ("d:/Antigravity/tavuk/core/adapters/registry.py", f"{project_dir}/core/adapters/registry.py"),
    ("d:/Antigravity/tavuk/database/config.py", f"{project_dir}/database/config.py"),
    ("d:/Antigravity/tavuk/database/models.py", f"{project_dir}/database/models.py"),
    ("d:/Antigravity/tavuk/api/main.py", f"{project_dir}/api/main.py"),
    ("d:/Antigravity/tavuk/frontend/templates/index.html", f"{project_dir}/frontend/templates/index.html"),
    ("d:/Antigravity/tavuk/frontend/templates/login.html", f"{project_dir}/frontend/templates/login.html"),
    ("d:/Antigravity/tavuk/frontend/templates/landing.html", f"{project_dir}/frontend/templates/landing.html"),
    ("d:/Antigravity/tavuk/frontend/templates/manual.html", f"{project_dir}/frontend/templates/manual.html"),
    ("d:/Antigravity/tavuk/frontend/static/js/main.js", f"{project_dir}/frontend/static/js/main.js"),
    ("d:/Antigravity/tavuk/frontend/static/og_cover.png", f"{project_dir}/frontend/static/og_cover.png"),
    ("d:/Antigravity/tavuk/docker-compose.yml", f"{project_dir}/docker-compose.yml"),
    ("d:/Antigravity/tavuk/mosquitto.conf", f"{project_dir}/mosquitto.conf"),
    ("d:/Antigravity/tavuk/requirements.txt", f"{project_dir}/requirements.txt"),
    ("d:/Antigravity/tavuk/Dockerfile", f"{project_dir}/Dockerfile"),
    ("d:/Antigravity/tavuk/mock_mqtt.py", f"{project_dir}/mock_mqtt.py"),
    ("d:/Antigravity/tavuk/mock_scada_controller.py", f"{project_dir}/mock_scada_controller.py"),
    ("d:/Antigravity/tavuk/.env", f"{project_dir}/.env")
]

for local_path, remote_path in files_to_upload:
    try:
        print(f"Uploading {local_path} -> {remote_path}")
        sftp.put(local_path, remote_path)
    except Exception as e:
        print(f"Skipped {local_path}: {e}")

sftp.close()

ssh.exec_command(f"cd {project_dir} && docker-compose build --no-cache web")
ssh.exec_command(f"cd {project_dir} && docker-compose build --no-cache mock_sensor")
ssh.exec_command(f"cd {project_dir} && docker-compose build --no-cache mock_scada")

print("Running PostgreSQL migration for demo_mode...")
stdin, stdout, stderr = ssh.exec_command("docker exec ciftlik_db_1 psql -U postgres -d ariot -c 'ALTER TABLE farm_settings ADD COLUMN IF NOT EXISTS demo_mode BOOLEAN DEFAULT FALSE;'")
print(stdout.read().decode())
print(stderr.read().decode())

print("Recreating ciftlik_web_1 ... ", end="", flush=True)

print("Rebuilding docker containers to apply postgres/mqtt changes...")
stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose up -d --build")
out_text = stdout.read().decode('utf-8', errors='replace')
err_text = stderr.read().decode('utf-8', errors='replace')

# Database schema changes should be handled by Alembic or manual migration, not by dropping tables.

try:
    print(out_text)
    print(err_text)
except UnicodeEncodeError:
    print(out_text.encode('ascii', 'replace').decode('ascii'))
    print(err_text.encode('ascii', 'replace').decode('ascii'))

ssh.close()
print("Deployment Complete.")
