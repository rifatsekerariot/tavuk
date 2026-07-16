import paramiko

host = '185.22.186.132'
user = 'root'
password = 'Qx9#Rz2#Fq8#Dd5!'
domain = 'ciftlik.rifatseker.com.tr'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Using sed to inject websocket headers safely into existing nginx config...")
sed_cmd = f"""sed -i '/proxy_set_header Host $host;/i \\        proxy_http_version 1.1;\\n        proxy_set_header Upgrade $http_upgrade;\\n        proxy_set_header Connection "upgrade";' /etc/nginx/sites-available/{domain}"""
stdin, stdout, stderr = ssh.exec_command(sed_cmd)
stdout.channel.recv_exit_status()

print("Reloading NGINX...")
stdin, stdout, stderr = ssh.exec_command("nginx -t && systemctl reload nginx")
stdout.channel.recv_exit_status()

ssh.close()
print("Done.")
