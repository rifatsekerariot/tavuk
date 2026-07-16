import paramiko

HOST = '185.22.186.132'
USER = 'root'
PASS = 'Qx9#Rz2#Fq8#Dd5!'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

stdin, out, err = ssh.exec_command('docker exec ciftlik_db_1 psql -U postgres -d ariot -c "SELECT demo_mode FROM farm_settings;"')
print('OUT:', out.read().decode())
print('ERR:', err.read().decode())

ssh.close()
