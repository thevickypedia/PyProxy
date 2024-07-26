import os
import socket
import sys
from ipaddress import IPv4Address
from typing import Dict, List, Set

from pydantic import BaseModel, HttpUrl, PositiveInt, field_validator
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


class RateLimit(BaseModel):
    """Object to store the rate limit settings.

    >>> RateLimit

    """

    max_requests: PositiveInt
    seconds: PositiveInt


class Session(BaseModel):
    """Object to store session information.

    >>> Session

    """

    rps: Dict[str, int] = {}
    allowed_origins: Set[str] = set()


class PublicAccess(StrEnum):
    """Enum for asterisk to indicate public access."""

    asterisk: str = "*"


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

    # Allows all headers by default
    allowed_headers: List[str] | PublicAccess = "*"
    allowed_origins: List[HttpUrl] | PublicAccess = []
    allowed_methods: List[AllowedMethods] | PublicAccess = [
        AllowedMethods.get,
        AllowedMethods.post,
    ]

    rate_limit: RateLimit | List[RateLimit] = []
    remove_headers: List[str] = []
    add_headers: List[Dict[str, str]] = [{}]

    # noinspection PyMethodParameters,PyUnusedLocal
    @field_validator("allowed_origins", mode="after", check_fields=True)
    def parse_allowed_origins(
        cls, allowed_origins: List[HttpUrl] | PublicAccess
    ) -> List[str]:
        """Validate allowed_origins' input as a URL, and stores only the host part of the URL."""
        # Can only be a list or URLs or *
        if isinstance(allowed_origins, list):
            return list(set([origin.host for origin in allowed_origins]))
        return allowed_origins

    # noinspection PyMethodParameters,PyUnusedLocal
    @field_validator("rate_limit", mode="after", check_fields=True)
    def parse_rate_limit(
        cls, rate_limit: RateLimit | List[RateLimit]
    ) -> List[RateLimit] | List:
        """Validate rate_limit and convert to list."""
        if isinstance(rate_limit, list):
            return rate_limit
        return [rate_limit]

    class Config:
        """Config for env vars."""

        env_file = os.environ.get("env_file", ".env")
        extra = "ignore"


# https://docs.pydantic.dev/2.6/errors/validation_errors/
# Expected behavior: https://github.com/pydantic/pydantic-core/issues/963#issuecomment-1832225195
validation_errors = []

settings = Settings()
session = Session()
