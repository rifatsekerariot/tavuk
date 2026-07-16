import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Starting docker containers again...")
stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose up -d --build")

out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')

print("OUT:", out)
print("ERR:", err)

ssh.close()
