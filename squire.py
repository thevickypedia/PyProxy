import socket
from ipaddress import IPv4Address

from pydantic import HttpUrl, PositiveInt, ValidationError
from pydantic_core import InitErrorDetails
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for environment variables."""

    # Hostname takes precendence to auto resolve IP address unless a client_url is provided
    client_host: str | None = None

    # IP address if known (less reliable in case of dyanmic IP addresses)
    client_ip: str | IPv4Address | None = None

    # Port number for the client service
    client_port: PositiveInt = 8080

    # Client URL will be constructed based on the information above
    client_url: HttpUrl | None = None

    class Config:
        """Config for env vars."""

        env_file = ".env"
        extra = "ignore"


# https://docs.pydantic.dev/2.6/errors/validation_errors/
# Expected behavior: https://github.com/pydantic/pydantic-core/issues/963#issuecomment-1832225195
validation_errors = []

settings = Settings()
if settings.client_url:
    settings.client_url = str(settings.client_url)
else:
    if not settings.client_port:
        ValidationError.from_exception_data(
            title="STRATEGY",
            line_errors=InitErrorDetails(
                type="int_type",
                loc=("client_port",),
                input="missing",
            ),
        )
    if settings.client_host:
        settings.client_ip = socket.gethostbyname(settings.client_host)
    if settings.client_ip:
        settings.client_url = str(
            HttpUrl(f"http://{settings.client_ip}:{settings.client_port}")
        )
    else:
        settings.client_url = str(
            HttpUrl(f"http://{settings.client_host}:{settings.client_port}")
        )
