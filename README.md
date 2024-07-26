# PyProxy
High speed proxy engine to serve light weight content

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

[license]: https://github.com/thevickypedia/pyfilebrowser/blob/main/LICENSE
[sphinx]: https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html
[google-docs]: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[pep8]: https://www.python.org/dev/peps/pep-0008/
[isort]: https://pycqa.github.io/isort/

[Rate limiting]: https://www.cloudflare.com/learning/bots/what-is-rate-limiting/
[DDoS]: https://www.cloudflare.com/learning/ddos/glossary/denial-of-service/
[Rate Limiter]: https://builtin.com/software-engineering-perspectives/rate-limiter
[Firewall]: https://www.zenarmor.com/docs/network-security-tutorials/what-is-proxy-firewall
