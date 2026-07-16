import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

sftp = ssh.open_sftp()
sftp.put("d:/Antigravity/tavuk/requirements.txt", f"{project_dir}/requirements.txt")
sftp.close()

print("Rebuilding Docker container on server...")
stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose up -d --build web")
exit_status = stdout.channel.recv_exit_status()

print("Output:")
print(stdout.read().decode())
print(stderr.read().decode())
print(f"Exit status: {exit_status}")

ssh.close()
