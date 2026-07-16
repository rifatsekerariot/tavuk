import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Clearing pycache...")
stdin, stdout, stderr = ssh.exec_command('find /var/www/ciftlik -name "__pycache__" -exec rm -rf {} +')
stdout.channel.recv_exit_status()

print("Restarting web container...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/ciftlik && docker compose restart web')
stdout.channel.recv_exit_status()

ssh.close()
print("Done.")
