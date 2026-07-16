import paramiko
import os

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Fetching docker logs for web container...")
stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose logs --tail 100 web")

out_text = stdout.read().decode('utf-8', errors='replace')
err_text = stderr.read().decode('utf-8', errors='replace')

try:
    print(out_text)
    if err_text:
        print("ERRORS:", err_text)
except UnicodeEncodeError:
    print(out_text.encode('ascii', 'replace').decode('ascii'))

print("-" * 50)
print("Fetching docker logs for mqtt container...")
stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose logs --tail 20 mqtt")
out_text2 = stdout.read().decode('utf-8', errors='replace')
try:
    print(out_text2)
except UnicodeEncodeError:
    print(out_text2.encode('ascii', 'replace').decode('ascii'))

ssh.close()
