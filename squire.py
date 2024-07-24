import socket

from ipaddress import IPv4Address
from pydantic import HttpUrl, PositiveInt
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    client_host: str | None = None
    client_ip: str | IPv4Address | None = None
    client_port: PositiveInt = 8080
    client_url: HttpUrl | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
if settings.client_host:
    settings.client_ip = socket.gethostbyname(settings.client_host)
