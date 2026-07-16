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
local_path = "d:/Antigravity/tavuk/frontend/static/js/map.js"
remote_path = f"{project_dir}/frontend/static/js/map.js"
sftp.put(local_path, remote_path)
sftp.close()
ssh.close()
print("map.js deployed successfully.")
