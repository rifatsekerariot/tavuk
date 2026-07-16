import paramiko
import os
import sys

def deploy():
    host = '185.22.186.132'
    user = 'root'
    password = 'Qx9#Rz2#Fq8#Dd5!'
    domain = 'ciftlik.rifatseker.com.tr'
    project_dir = '/var/www/ciftlik'
    
    print("Connecting to Motozeka Server via SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)
        
    print(f"Creating directory {project_dir}...")
    ssh.exec_command(f"mkdir -p {project_dir}")
    
    print("Uploading deploy.tar.gz...")
    sftp = ssh.open_sftp()
    local_tar = r"d:\Antigravity\tavuk\deploy.tar.gz"
    remote_tar = f"{project_dir}/deploy.tar.gz"
    sftp.put(local_tar, remote_tar)
    
    print("Extracting files...")
    stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && tar -xzf deploy.tar.gz")
    stdout.channel.recv_exit_status()
    
    print("Checking NGINX config...")
    stdin, stdout, stderr = ssh.exec_command(f"test -f /etc/nginx/sites-available/{domain} && echo 'exists'")
    if "exists" not in stdout.read().decode():
        nginx_conf = f'''server {{
    listen 80;
    server_name {domain};

    location / {{
        proxy_pass http://127.0.0.1:9030;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
'''
        print("Creating NGINX config...")
        stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/nginx/sites-available/{domain}")
        stdin.write(nginx_conf)
        stdin.close()
        stdout.channel.recv_exit_status()
        ssh.exec_command(f"ln -sf /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/{domain}")
    else:
        print("NGINX config already exists.")

    print("Fixing docker-compose ports to bind to 9030...")
    sed_cmd = f"sed -i 's/- \"8000:8000\"/- \"127.0.0.1:9030:8000\"/' {project_dir}/docker-compose.yml"
    ssh.exec_command(sed_cmd)

    print("Starting docker containers...")
    stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose up -d --build")
    for line in iter(stdout.readline, ""):
        print(line, end="")
    for line in iter(stderr.readline, ""):
        print(line, end="")
    stdout.channel.recv_exit_status()

    print("Reloading NGINX...")
    stdin, stdout, stderr = ssh.exec_command("nginx -t && systemctl reload nginx")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    print("Installing SSL Certificate...")
    cert_cmd = f"certbot --nginx -d {domain} --non-interactive --agree-tos -m admin@rifatseker.com.tr --redirect"
    stdin, stdout, stderr = ssh.exec_command(cert_cmd)
    for line in iter(stdout.readline, ""):
        print(line, end="")
    for line in iter(stderr.readline, ""):
        print(line, end="")
    stdout.channel.recv_exit_status()

    sftp.close()
    ssh.close()
    print("Deployment complete!")

if __name__ == '__main__':
    deploy()
