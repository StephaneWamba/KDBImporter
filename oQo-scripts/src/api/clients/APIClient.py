from typing import Any, Mapping, MutableMapping, Optional, Union
from urllib.parse import urlencode, urljoin
import requests # type: ignore

from config import get_logger
from ..Sleeper import Sleeper

JSON = Union[dict[str, Any], list, str, int, float, bool, None]
logger = get_logger("Logger4ScrappingoQo")

# import http.client as _http_client, logging, sys
# _http_client.HTTPConnection.debuglevel = 1    # dump brut des requêtes
# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class APIClient(Sleeper):
    base_url: str = ""
    default_headers: Mapping[str, str] = {}
    
    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
        idle_time: float = 0.0,
        random_idle_time: bool = False,
        parse_json: bool = True,
        timeout: int = 30,
    ) -> None:
        super().__init__(idle_time, random_idle_time)

        if base_url is not None:
            self.base_url = base_url.rstrip("/")

        self.parse_json = parse_json
        self.timeout = timeout

        self.headers: MutableMapping[str, str] = {
            **self.default_headers,
            **(headers or {}),
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)
            
    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[JSON] = None,
        data: Optional[Mapping[str, Any]] = None,
        files: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        parse_json: Optional[bool] = None,
    ) -> Any:
        url   = urljoin(f"{self.base_url}/", endpoint.lstrip("/"))
        hdrs  = {**self.session.headers, **(headers or {})}

        self.time_action()

        resp  = self.session.request(
            method=method.upper(),
            url=url,
            headers=hdrs,
            params=params,
            json=json, data=data, files=files,
            timeout=self.timeout,
            verify=getattr(self, "verify_ssl", True),
        )
        
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exception:
            status = exception.response.status_code
            body = exception.response.text.strip()
            logger.error(f"HTTP {status} on {url} - Body:\n{body}")
        
        except requests.exceptions.RequestException as exc:
            logger.error("Request failed on %s — %s", url, exc)
            raise

        
        should_parse = self.parse_json if parse_json is None else parse_json
        
        if should_parse:
            try:
                return resp.json()
            except ValueError:
                return resp.text

        return resp.content

    def get(self, endpoint: str, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs):
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs):
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)