import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

stdin, stdout, stderr = ssh.exec_command('docker exec ciftlik_web_1 python -c "from api.main import app; print([r.path for r in app.routes])"')
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
