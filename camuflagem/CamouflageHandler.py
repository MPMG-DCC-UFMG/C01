from os import system

class CamouflageHandler:
    def __init__(self, tor_host: str ='127.0.0.1', tor_port: int=9050):
        self.tor_host = tor_host
        self.tor_port = tor_port

    def renew_ip(self) -> None:
        system('sudo service tor reload')