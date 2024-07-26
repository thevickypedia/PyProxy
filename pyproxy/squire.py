import socket

from pydantic import HttpUrl, ValidationError
from pydantic_core import InitErrorDetails

from pyproxy.config import PublicAccess, RateLimit, session, settings  # noqa: F401

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

if settings.allowed_origins == PublicAccess.asterisk:
    session.allowed_origins = "*"
else:
    session.allowed_origins.add(settings.proxy_host)
    session.allowed_origins.update(settings.allowed_origins)
    if settings.proxy_host == socket.gethostbyname("localhost"):
        session.allowed_origins.add("localhost")
        session.allowed_origins.add("0.0.0.0")
    session.allowed_origins = list(session.allowed_origins)
