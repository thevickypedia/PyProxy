import logging
from contextlib import asynccontextmanager
from http import HTTPStatus

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from pyproxy.squire import settings

LOGGER = logging.getLogger("uvicorn.error")
CLIENT = httpx.Client()  # Create re-usable client object


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function to handle startup and shutdown events."""
    LOGGER.info(
        "Tunneling http://%s:%d -> %s",
        settings.proxy_host,
        settings.proxy_port,
        settings.client_url,
    )
    yield
    LOGGER.info("Stopped tunneling")


async def proxy(request: Request) -> Response:
    """Proxy handler function to forward incoming requests to a target URL.

    Args:
        request: The incoming request object.

    Returns:
        Response: The response object with the forwarded content and headers.
    """
    try:
        body = await request.body()
        # noinspection PyTypeChecker
        response = CLIENT.request(
            method=request.method,
            url=settings.client_url + request.url.path,
            headers=dict(request.headers),
            cookies=request.cookies,
            params=dict(request.query_params),
            data=body,
            follow_redirects=True,
        )
        headers = response.headers.copy()
        content_type = headers.get("content-type", "")
        if "text" in content_type:
            content = response.text
        else:
            content = response.content
        # headers.pop("host", None)
        # headers.pop("content-length", None)
        # headers.pop("accept-encoding", None)
        # headers.pop("content-encoding", None)
        return Response(content, response.status_code, headers, content_type)
    except httpx.RequestError as exc:
        LOGGER.error(exc)
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY.value,
            detail=HTTPStatus.BAD_GATEWAY.phrase,
        )


def main():
    """Server handler."""
    # todo:
    #   Include a repeated timer to update the client_url
    #   Take refresh_interval as an env var and default to 15 minutes
    #       Do this only if it was constructed by PyProxy
    #   Include file logger
    app = FastAPI(
        routes=[
            APIRoute(
                "/{_:path}",
                methods=settings.allowed_methods,
                endpoint=proxy,
            )
        ],
        lifespan=lifespan,
    )
    # noinspection PyTypeChecker
    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",  # todo: restrict if need be
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers="*",  # todo: restrict if need be
        max_age=300,  # maximum time in seconds for browsers to cache CORS responses
    )
    uvicorn.run(host=settings.proxy_host, port=settings.proxy_port, app=app)
