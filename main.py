import logging
from http import HTTPStatus

import httpx
import uvicorn.logging
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.routing import APIRoute

from squire import settings

CLIENT = httpx.Client()  # Create re-usable client object


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
            data=body.decode(),
        )

        # If the response content-type is text/html, we need to rewrite links in it
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type:
            content = response.text
            # Modify content if necessary (e.g., rewriting links)
            # content = modify_html_links(content)
        else:
            content = response.content
        response.headers.pop("content-encoding", None)

        return Response(content, response.status_code, response.headers, content_type)
    except httpx.RequestError as exc:
        logging.getLogger("uvicorn.error").error(exc)
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY.value,
            detail=HTTPStatus.BAD_GATEWAY.phrase,
        )


if __name__ == "__main__":
    print(settings.client_ip)
    print(settings.client_host)
    exit(0)
    uvicorn.run(
        app=FastAPI(
            routes=[
                APIRoute(
                    "/{_:path}",
                    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                    endpoint=proxy,
                )
            ]
        )
    )
