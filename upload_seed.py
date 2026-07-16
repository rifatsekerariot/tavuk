import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

sftp = ssh.open_sftp()
sftp.put("d:/Antigravity/tavuk/seed_history.py", f"{project_dir}/seed_history.py")
sftp.close()

stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose exec -T web python seed_history.py")
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
print("Seeding complete.")
