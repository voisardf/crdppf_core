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


import urllib
import logging

import simplejson as json


from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadGateway

from print_project.views.proxy import Proxy

from print_project.util.cached_content import get_cached_content, get_cached_content_l10n
from print_project.util.content import get_content

log = logging.getLogger(__name__)



class PrintProxy(Proxy):  # pragma: no cover

    def __init__(self, request):
        Proxy.__init__(self, request)
        self.config = self.request.registry.settings

    @view_config(route_name='printproxy_report_create')
    def report_create(self):
        """ Create PDF. """
        
        content = {
            "layout": "report",
            "outputFormat": "pdf",
            "attributes": {}
        }
        content["attributes"].update(get_cached_content())
        content["attributes"].update(get_cached_content_l10n(self.request.params.get(
            "lang",
            self.request.registry.settings["lang"]
        )))
        content["attributes"].update(get_content(self.request.matchdict.get("ref")))
        
        return self._proxy_response(
            "print",
            "%s/report.%s" % (
                self.config['print_url'],
                "pdf"
            ),
            body=json.dumps(content)
        )

    @view_config(route_name='printproxy_status')
    def status(self):
        """ PDF status. """
        return self._proxy_response(
            "print",
            "%s/status/%s.json" % (
                self.config['print_url'],
                self.request.matchdict.get('ref')
            ),
        )

    @view_config(route_name='printproxy_report_get')
    def report_get(self):
        """ Get the PDF. """
        return self._proxy_response(
            "print",
            "%s/report/%s" % (
                self.config['print_url'],
                self.request.matchdict.get('ref')
            ),
        )
