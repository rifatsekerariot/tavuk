import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Starting mock_mqtt.py inside web container...")
stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose exec -d web python mock_mqtt.py")

out_text = stdout.read().decode('utf-8', errors='replace')
err_text = stderr.read().decode('utf-8', errors='replace')

try:
    print(out_text)
    if err_text:
        print("ERRORS:", err_text)
except UnicodeEncodeError:
    pass

ssh.close()
print("Done.")
