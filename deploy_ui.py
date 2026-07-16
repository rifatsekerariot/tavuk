import paramiko
import os

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

sftp = ssh.open_sftp()
files = [
    ("frontend/templates/index.html", "frontend/templates/index.html"),
    ("frontend/templates/landing.html", "frontend/templates/landing.html"),
    ("frontend/static/js/main.js", "frontend/static/js/main.js"),
    ("api/main.py", "api/main.py"),
    ("core/biology.py", "core/biology.py"),
    ("frontend/static/asset1.png", "frontend/static/asset1.png"),
    ("frontend/static/asset2.png", "frontend/static/asset2.png")
]

for local_f, remote_f in files:
    sftp.put(f"d:/Antigravity/tavuk/{local_f}", f"{project_dir}/{remote_f}")

sftp.close()

commands = [
    f"cd {project_dir} && docker compose cp frontend/templates/index.html web:/app/frontend/templates/index.html",
    f"cd {project_dir} && docker compose cp frontend/templates/landing.html web:/app/frontend/templates/landing.html",
    f"cd {project_dir} && docker compose cp frontend/static/js/main.js web:/app/frontend/static/js/main.js",
    f"cd {project_dir} && docker compose cp api/main.py web:/app/api/main.py",
    f"cd {project_dir} && docker compose restart web"
]

for cmd in commands:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()  # Wait for command to finish

ssh.close()
print("UI and API deployed successfully.")
