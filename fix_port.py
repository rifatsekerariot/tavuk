import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
project_dir = '/var/www/ciftlik'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Fix docker-compose port to 9040
ssh.exec_command(f"sed -i 's/127.0.0.1:9030:8000/127.0.0.1:9040:8000/' {project_dir}/docker-compose.yml")

# Fix nginx proxy_pass to 9040
ssh.exec_command("sed -i 's/proxy_pass http:\/\/127.0.0.1:9030;/proxy_pass http:\/\/127.0.0.1:9040;/' /etc/nginx/sites-available/ciftlik.rifatseker.com.tr")

# Restart nginx
ssh.exec_command("systemctl reload nginx")

# Restart docker
ssh.exec_command(f"cd {project_dir} && docker-compose up -d")

ssh.close()
