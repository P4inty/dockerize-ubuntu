from fabric import Connection
from registry.registry import Registry

class Server:
    def __init__(self, ip, key_filename, registry = Registry() ,root='root', docker_user='moby_dock'):
        self.ip = ip
        self.key_filename = key_filename
        self.root = root
        self.docker_user = docker_user
        self.connection = None
        self.registry = registry
    
    def create_user(self):
        self.connection.sudo(f"adduser --disabled-password --gecos '' {self.docker_user}")
        self.connection.sudo(f'usermod -aG sudo {self.docker_user}')
        self.connection.run(f'rsync --archive --chown={self.docker_user}:{self.docker_user} ~/.ssh /home/{self.docker_user}')

    def firewall(self):
        self.connection.run('ufw allow OpenSSH')
        self.connection.run('yes | ufw enable')

    def disable_pw_auth(self):
        self.connection.run("sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config")
        self.connection.sudo('systemctl reload sshd')
        self.connection.run(f"echo '{self.docker_user} ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/{self.docker_user}")

    def update(self):
        self.connection.sudo('apt update -y')
        self.connection.sudo('apt upgrade -y')

    def docker(self):
        self.connection.sudo('apt install apt-transport-https ca-certificates curl software-properties-common git -y')
        self.connection.sudo('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -')
        self.connection.sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')
        self.update()
        self.connection.sudo('apt-cache policy docker-ce')
        self.connection.sudo('apt install docker-ce docker-compose -y')
        self.connection.sudo('usermod -aG docker ${USER}')

    def setup(self):
        self.connection = Connection(self.ip, self.root, connect_kwargs={'key_filename': f'{self.key_filename}'})
        self.create_user()
        self.disable_pw_auth()
        self.firewall()
        self.update()
        self.connection.close()
        self.connection = Connection(self.ip, self.docker_user, connect_kwargs={'key_filename': f'{self.key_filename}'})
        self.docker()
        self.connection.close()
        self.connection = Connection(self.ip, self.docker_user, connect_kwargs={'key_filename': f'{self.key_filename}'})
        self.registry.setup(self.connection)
        self.connection.close()