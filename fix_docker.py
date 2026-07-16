import paramiko
import sys

def fix():
    host = '185.22.186.132'
    user = 'root'
    password = 'Qx9#Rz2#Fq8#Dd5!'
    project_dir = '/var/www/ciftlik'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    print("Fixing docker-compose version to 3.3...")
    ssh.exec_command(f"sed -i 's/version: .*/version: \"3.3\"/' {project_dir}/docker-compose.yml")
    
    print("Starting docker containers again...")
    stdin, stdout, stderr = ssh.exec_command(f"cd {project_dir} && docker-compose up -d --build")
    for line in iter(stdout.readline, ""):
        print(line, end="")
    for line in iter(stderr.readline, ""):
        print(line, end="")
        
    ssh.close()

if __name__ == '__main__':
    fix()
