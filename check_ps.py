import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose ps -a && docker-compose logs")
print(stdout.read().decode('utf-8', errors='ignore'))
print(stderr.read().decode('utf-8', errors='ignore'))
ssh.close()
