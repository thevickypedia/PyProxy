import logging
from contextlib import asynccontextmanager
from http import HTTPStatus
from urllib.parse import urljoin

import httpx
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from pyproxy.postman import async_manager, sync_manager
from pyproxy.rate_limit import RateLimiter
from pyproxy.squire import session, settings

LOGGER = logging.getLogger("uvicorn.error")
if settings.async_proxy:
    HANDLER = async_manager
else:
    HANDLER = sync_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan function to handle startup and shutdown events."""
    LOGGER.info(
        "Tunneling http://%s:%d → %s, async_proxy: %s",
        settings.proxy_host,
        settings.proxy_port,
        settings.client_url,
        settings.async_proxy,
    )
    yield
    LOGGER.info("Stopped tunneling")


async def engine(request: Request) -> Response:
    """Proxy handler function to forward incoming requests to a target URL.

    Args:
        request: The incoming request object.

    Returns:
        Response: The response object with the forwarded content and headers.
    """
    # Since host header can be overridden, always check with base_url
    if (
        session.allowed_origins != "*"
        and request.base_url.hostname not in session.allowed_origins
    ):
        LOGGER.warning(
            "%s is blocked by firewall, since it is not set in allowed origins %s",
            request.base_url,
            session.allowed_origins,
        )
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN.value,
            detail=f"{request.base_url!r} is not allowed",
        )
    try:
        payload = dict(
            method=request.method,
            url=urljoin(settings.client_url, request.url.path),
            headers=dict(request.headers),
            cookies=request.cookies,
            params=dict(request.query_params),
            data=await request.body(),
        )
        response = await HANDLER(payload)
        headers = response.headers.copy()
        content_type = headers.get("content-type", "")
        if "text" in content_type:
            content = response.text
        else:
            content = response.content
        for header in settings.remove_headers:
            LOGGER.debug("Removing header: %s", header)
            headers.pop(header, None)
        for header in settings.add_headers:
            for key, value in header.items():
                LOGGER.debug("Adding header: %s", key)
                headers[key] = value
        return Response(content, response.status_code, headers, content_type)
    except httpx.RequestError as exc:
        LOGGER.error(exc)
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY.value,
            detail=HTTPStatus.BAD_GATEWAY.phrase,
        )


def run():
    """Server handler."""
    # todo:
    #   Include file logger
    settings.client_url = str(settings.client_url)

    dependencies = []
    for each_rate_limit in settings.rate_limit:
        LOGGER.info("Adding rate limit: %s", each_rate_limit)
        dependencies.append(Depends(dependency=RateLimiter(each_rate_limit).init))

    app = FastAPI(
        routes=[
            APIRoute(
                path="/{_:path}",
                endpoint=engine,
                methods=settings.allowed_methods,
                dependencies=dependencies,
            )
        ],
        lifespan=lifespan,
    )
    # noinspection PyTypeChecker
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
        max_age=300,  # maximum time in seconds for browsers to cache CORS responses
    )
    uvicorn.run(host=settings.proxy_host, port=settings.proxy_port, app=app)
