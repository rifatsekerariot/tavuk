import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose up -d --build > build.log 2>&1")
stdout.channel.recv_exit_status()

stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && cat build.log")
print(stdout.read().decode('utf-8', errors='ignore'))
ssh.close()
