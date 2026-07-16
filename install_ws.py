import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Installing websockets in web container...")
stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker compose exec -T web pip install websockets")
out = stdout.read()
print(out.decode('utf-8', errors='replace'))

print("Restarting web container...")
stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker compose restart web")
out = stdout.read()
print(out.decode('utf-8', errors='replace'))

ssh.close()
print("Done.")
