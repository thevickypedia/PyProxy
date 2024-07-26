# PyProxy
High speed proxy engine to serve light weight content

## Environment Variables
Env vars can either be loaded from `.env` files.

<details>
<summary><strong>Env Requirements</strong></summary>

- **proxy_host** `str` - Hostname/IP for the proxy server. _Defaults to `socket.gethostbyname('localhost')`_
- **proxy_port** `int` - Port number for the proxy server. _Defaults to `8000`_
- **async_proxy** `bool` - Enables asynchronous requests to the client. _Defaults to `False`_
- **client_host** `str` - Hostname of the client server. _Defaults to `None`_
- **client_ip** `IPv4Address` - IP address of the client server. _Defaults to `None`_
- **client_port** `int` - Port number of the client server. _Defaults to `None`_
- **client_url** `HttpUrl` - Direct URL to the client server. _Defaults to `None`_
- **allowed_headers** `List[str]` - Headers to allow via CORS. _Defaults to `*`_
- **allowed_origins** `List[str]` - Origins to allow connections through proxy server and CORS. _Defaults to `host`_
- **allowed_methods** `List[str]` - HTTP methods to allow through proxy server. _Defaults to `["GET", "POST"]`_
- **rate_limit** `Dict/List[Dict]` with the rate limit for the proxy server. _Defaults to `None`_
- **remove_headers** `List[str]` - Client headers that has to be removed before rendering the response. 
- **add_headers** `List[Dict[str, str]]` - Headers to be added before rendering the response.

> `add_headers` and `remove_headers` are executed ONLY after the response is received from the client. This will NOT alter any transaction between `pyproxy` and the client.
</details>

<br>

> PyProxy may increase an inconspicuous latency to the connections,
> but due to asynchronous functionality, it is hardly noticeable.<br>
> The proxy server is designed to be lightweight and efficient, however streaming large video files may increase
> the memory usage at server side, due to multi-layered buffering.

### [Firewall]

While CORS may solve the purpose at the webpage level, the built-in proxy's firewall restricts connections
from any origin regardless of the tool used to connect (PostMan, curl, wget etc.)

Due to this behavior, please make sure to specify **ALL** the origins that are supposed to be allowed
(including but not limited to reverse-proxy, CDN, redirect servers etc.)

### [Rate Limiter]
The built-in proxy service allows you to implement a rate limiter.

[Rate limiting] allows you to prevent [DDoS] attacks and maintain server stability and performance.

## Coding Standards
Docstring format: [`Google`][google-docs] <br>
Styling conventions: [`PEP 8`][pep8] and [`isort`][isort]

## Linting
`pre-commit` is used to ensure linting.

```shell
pre-commit run --all-files
```

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License][license]

[license]: https://github.com/thevickypedia/pyproxy/blob/main/LICENSE
[sphinx]: https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html
[google-docs]: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[pep8]: https://www.python.org/dev/peps/pep-0008/
[isort]: https://pycqa.github.io/isort/

[Rate limiting]: https://www.cloudflare.com/learning/bots/what-is-rate-limiting/
[DDoS]: https://www.cloudflare.com/learning/ddos/glossary/denial-of-service/
[Rate Limiter]: https://builtin.com/software-engineering-perspectives/rate-limiter
[Firewall]: https://www.zenarmor.com/docs/network-security-tutorials/what-is-proxy-firewall
