import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

sftp = ssh.open_sftp()
local_file = r"d:\Antigravity\tavuk\frontend\templates\index.html"
remote_file = f"{project_dir}/frontend/templates/index.html"
sftp.put(local_file, remote_file)
sftp.close()

# No need to restart docker because templates are reloaded by Jinja or Uvicorn on each request (if reload=True or just template rendering). But to be safe let's restart the container.
ssh.exec_command(f"cd {project_dir} && docker-compose restart web")
ssh.close()
