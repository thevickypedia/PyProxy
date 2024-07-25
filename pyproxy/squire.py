import os
import socket
from ipaddress import IPv4Address
import sys
from typing import List

from pydantic import HttpUrl, PositiveInt, ValidationError
from pydantic_core import InitErrorDetails
from pydantic_settings import BaseSettings


if sys.version_info.minor > 10:
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Override for python 3.10 due to lack of StrEnum."""


class AllowedMethods(StrEnum):
    get: str = "GET"
    put: str = "PUT"
    post: str = "POST"
    head: str = "HEAD"
    patch: str = "PATCH"
    delete: str = "DELETE"
    options: str = "OPTIONS"


class Settings(BaseSettings):
    """Settings for environment variables."""

    proxy_host: str = socket.gethostbyname("localhost")
    proxy_port: PositiveInt = 8000
    workers: PositiveInt = int(os.cpu_count() / 2)

    # Hostname takes precendence to auto resolve IP address unless a client_url is provided
    client_host: str | None = None

    # IP address if known (less reliable in case of dyanmic IP addresses)
    client_ip: str | IPv4Address | None = None

    # Port number for the client service
    client_port: PositiveInt | None = None

    # Client URL will be constructed based on the information above
    client_url: HttpUrl | None = None

    allowed_methods: List[AllowedMethods] = [AllowedMethods.get, AllowedMethods.post]

    class Config:
        """Config for env vars."""

        env_file = os.environ.get("env_file", ".env")
        extra = "ignore"


# https://docs.pydantic.dev/2.6/errors/validation_errors/
# Expected behavior: https://github.com/pydantic/pydantic-core/issues/963#issuecomment-1832225195
validation_errors = []

settings = Settings()
if settings.client_url:
    settings.client_url = str(settings.client_url)
else:
    if not settings.client_port:
        raise ValidationError.from_exception_data(
            title="client_port",
            line_errors=[
                InitErrorDetails(
                    type="int_type",
                    loc=("client_port",),
                    input="missing",
                )
            ],
        )

    if not any((settings.client_ip, settings.client_host)):
        raise ValidationError.from_exception_data(
            title="value_error",
            line_errors=[
                InitErrorDetails(
                    type="string_type",
                    loc=("client_ip",),
                    input="missing",
                ),
                InitErrorDetails(
                    type="string_type",
                    loc=("client_host",),
                    input="missing",
                ),
            ],
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
