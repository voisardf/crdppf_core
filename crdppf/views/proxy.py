# -*- coding: utf-8 -*-

# Copyright (c) 2011-2015, Camptocamp SA
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.


import sys
import httplib2
import urllib
import logging

from io import StringIO

from urllib.parse import urlparse, parse_qs, urlencode

from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadGateway, HTTPInternalServerError

log = logging.getLogger(__name__)


class Proxy:

    def __init__(self, request):
        self.request = request

    def _proxy(self, url, params=None, method=None, body=None, headers=None):
        # get query string

        params = dict(self.request.params) if params is None else params
        parsed_url = urlparse(url)
        all_params = parse_qs(parsed_url.query)

        for p in all_params:
            all_params[p] = ",".join(all_params[p])
        all_params.update(params)
        params_encoded = {}

        query_string = urlencode(all_params)

        if parsed_url.port is None:
            url = "%s://%s%s?%s" % (
                parsed_url.scheme, parsed_url.hostname,
                parsed_url.path, query_string
            )
        else:  # pragma: nocover
            url = "%s://%s:%i%s?%s" % (
                parsed_url.scheme, parsed_url.hostname, parsed_url.port,
                parsed_url.path, query_string
            )

        log.info("Send query to URL:\n%s." % url)

        if method is None:
            method = self.request.method

        # forward request to target (without Host Header)
        http = httplib2.Http()
        if headers is None:  # pragma: nocover
            headers = dict(self.request.headers)
            if parsed_url.hostname != "localhost":
                headers.pop("Host")

        headers["Cache-Control"] = "no-cache"
  
        # Other problematic headers
        for header in [
            "Content-Length",
            "Content-Location",
            "Content-Encoding",
        ]:  # pragma: no cover
            if header in headers:
                del headers[header]

        if method in ["POST", "PUT"] and body is None:  # pragma: nocover
            body = StringIO(self.request.body)

        try:
            if method in ["POST", "PUT"]:
                resp, content = http.request(
                    url, method=method, body=body, headers=headers
                )
            else:
                resp, content = http.request(
                    url, method=method, headers=headers
                )
        except Exception as e:  # pragma: nocover
            log.error(
                "Error '%s' while getting the URL:\n%s\nMethode: %s." %
                (sys.exc_info()[0], url, method)
            )

            log.error(
                "--- With headers ---\n%s" %
                "\n".join(["%s: %s" % h for h in headers.items()])
            )

            log.error("--- Exception ---")
            log.exception(e)

            if method in ["POST", "PUT"]:
                log.error("--- With body ---")
                if hasattr(body, "read"):
                    body.reset()
                    log.error(body.read())
                else:
                    log.error(body)

            raise HTTPBadGateway("See logs for detail")

        if resp.status < 200 or resp.status >= 300:  # pragma: no cover
            log.error(
                "Error '%s' in response of URL:\n%s." %
                (resp.reason, url)
            )

            log.error("Status: %i" % resp.status)
            log.error("Method: %s" % method)

            log.error(
                "--- With headers ---\n%s" %
                "\n".join(["%s: %s" % h for h in headers.items()])
            )

            if method == "POST":
                log.error("--- Query with body ---")
                if hasattr(body, "read"):
                    body.reset()
                    log.error(body.read())
                else:
                    log.error(body)

            log.error("--- Return content ---")
            log.error(content)

            raise HTTPInternalServerError("See logs for details")

        return resp, content

    def _proxy_response(
        self, url, headers=None, headers_update={}, **kwargs
    ):  # pragma: no cover

        resp, content = self._proxy(url, headers=headers, **kwargs)

        return self._build_response(
            resp, content, headers_update=headers_update
        )

    def _add_cors(self, headers):
        headers.update({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "X-Requested-With, Content-Type"
        })

    def _build_response(
        self, resp, content, headers=None, headers_update={}
    ):
        headers = dict(resp) if headers is None else headers

        if "content-length" in headers:  # pragma: no cover
            del headers["content-length"]
        if "transfer-encoding" in headers:  # pragma: no cover
            del headers["transfer-encoding"]
        if "content-location" in headers:  # pragma: no cover
            del headers["content-location"]

        self._add_cors(headers)

        headers.update(headers_update)

        response = Response(content, status=resp.status, headers=headers)
        response.cache_control.no_cache = True
        return response
