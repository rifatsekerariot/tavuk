import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.22.186.132', username='root', password='Qx9#Rz2#Fq8#Dd5!')

cmds = [
    'docker exec ciftlik_db_1 psql -U postgres -d ariot -c "DROP TABLE farm_settings;"',
    'docker restart ciftlik_web_1'
]

for cmd in cmds:
    print("Running:", cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())

ssh.close()
