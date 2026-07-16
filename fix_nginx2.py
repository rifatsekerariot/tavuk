import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

sftp = ssh.open_sftp()
with sftp.file('/etc/nginx/sites-available/ciftlik.rifatseker.com.tr', 'r') as f:
    content = f.read().decode('utf-8')

# Remove any duplicates manually by just rewriting the location block correctly
new_location = """    location / {
        proxy_pass http://127.0.0.1:9040;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }"""

import re
# Find the entire location / block and replace it
content = re.sub(r'    location / \{.*?\n    \}', new_location, content, flags=re.DOTALL)

with sftp.file('/etc/nginx/sites-available/ciftlik.rifatseker.com.tr', 'w') as f:
    f.write(content)

print(ssh.exec_command('nginx -t && systemctl restart nginx')[1].read().decode())
print(ssh.exec_command('nginx -t && systemctl restart nginx')[2].read().decode())
