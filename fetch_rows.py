import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.22.186.132', username='root', password='Qx9#Rz2#Fq8#Dd5!')

cmd = 'docker exec ciftlik_db_1 psql -U postgres -d ariot -c "SELECT id, timestamp, t_in, zone_id FROM iot_data ORDER BY timestamp DESC LIMIT 5;"'
stdin, stdout, stderr = ssh.exec_command(cmd)
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
