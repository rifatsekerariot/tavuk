import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

sftp = ssh.open_sftp()
sftp.put("d:/Antigravity/tavuk/frontend/templates/index.html", f"{project_dir}/frontend/templates/index.html")
sftp.put("d:/Antigravity/tavuk/frontend/static/js/main.js", f"{project_dir}/frontend/static/js/main.js")
sftp.close()
ssh.close()
print("UI files updated!")
