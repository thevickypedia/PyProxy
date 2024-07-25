import httpx
from httpx import Response

CLIENT = httpx.Client()  # Create re-usable client object


async def async_manager(payload: dict) -> Response:
    """Handles incoming requests with an asynchronous ``httpx`` client.

    See Also:
        Cannot reopen a client instance, once it has been closed.
    """
    async with httpx.AsyncClient() as client:
        return await client.request(**payload)


async def sync_manager(payload: dict) -> Response:
    """Reuses existing ``httpx`` client instance."""
    return CLIENT.request(**payload)
