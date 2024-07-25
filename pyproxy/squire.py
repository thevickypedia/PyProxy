import os
import socket
import sys
from ipaddress import IPv4Address
from typing import Dict, List

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
    """Enum for HTTP methods."""

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
    async_proxy: bool = False

    # Hostname takes precedence to auto resolve IP address unless a client_url is provided
    client_host: str | None = None

    # IP address if known (less reliable in case of dynamic IP addresses)
    client_ip: str | IPv4Address | None = None

    # Port number for the client service
    client_port: PositiveInt | None = None

    # Client URL will be constructed based on the information above
    client_url: HttpUrl | None = None

    allowed_origins: List[str] | str = "*"
    allowed_headers: List[str] | str = "*"
    allowed_methods: List[AllowedMethods] | str = [
        AllowedMethods.get,
        AllowedMethods.post,
    ]
    remove_headers: List[str] = []
    add_headers: List[Dict[str, str]] = [{}]

    class Config:
        """Config for env vars."""

        env_file = os.environ.get("env_file", ".env")
        extra = "ignore"


# https://docs.pydantic.dev/2.6/errors/validation_errors/
# Expected behavior: https://github.com/pydantic/pydantic-core/issues/963#issuecomment-1832225195
validation_errors = []

settings = Settings()
if not settings.client_url:
    errors = []
    if not settings.client_port:
        errors.append(
            InitErrorDetails(
                type="int_type",
                loc=("client_port",),
                input="missing",
            )
        )

    if not any((settings.client_ip, settings.client_host)):
        errors.extend(
            [
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
            ]
        )

    if errors:
        raise ValidationError.from_exception_data(title="PyProxy", line_errors=errors)

    if settings.client_host:
        settings.client_ip = socket.gethostbyname(settings.client_host)

    if settings.client_ip:
        settings.client_url = HttpUrl(
            f"http://{settings.client_ip}:{settings.client_port}"
        )
    else:
        settings.client_url = HttpUrl(
            f"http://{settings.client_host}:{settings.client_port}"
        )
