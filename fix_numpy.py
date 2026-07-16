import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Patching requirements.txt...")
# append numpy<2 if it's not already there or replace it. Just appending is fine if there isn't a strict version conflict.
ssh.exec_command(f"echo 'numpy<2' >> {project_dir}/requirements.txt")

print("Rebuilding docker...")
stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose build --no-cache && docker-compose up -d")
stdout.channel.recv_exit_status()

ssh.close()
