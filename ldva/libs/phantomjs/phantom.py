"""
Copyright (C) 2014 Kompetenzzentrum fuer wissensbasierte Anwendungen und Systeme
Forschungs- und Entwicklungs GmbH (Know-Center), Graz, Austria
office@know-center.at

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import subprocess
import hashlib
from django.http import HttpResponse
from subprocess import Popen, PIPE, STDOUT
import urllib

def vismage_capture(request):
    dataset = request.GET.get('dataset')
    endpoint = request.GET.get('endpoint')

    if dataset is not None and dataset != '':
        host = request.META['HTTP_HOST']
        url = 'http://' + host + '/vis#?dataset=' + urllib.quote_plus(dataset) + '&endpoint=' + endpoint + '&chartsonly=true'
    else:
        response = HttpResponse()
        response.status_code = 404
        return response

    return phantom_capture(request, url)


def phantom_capture(request, urlOverwrite=''):
    url = request.GET.get('url')
    if urlOverwrite != '':
        url = urlOverwrite

    if url is None or url == '':
        response = HttpResponse()
        response.status_code = 404
        return response

    host = request.META['HTTP_HOST']
    if not (host.startswith('127.0.0.1') or
        host.startswith('localhost') or
        host.endswith('know-center.tugraz.at')):
            response = HttpResponse()
            response.status_code = 403
            return response

    urlEncoded = url.encode('utf-8')
    filename = hashlib.md5(urlEncoded).hexdigest()
    fileNamePath = os.path.join(os.path.dirname(__file__), '../../../../code_vis_screenshots/') + filename + '.png'

    if not os.path.exists(fileNamePath):
        # windows: put phantomjs.exe to source-root;
        external_process = Popen(['phantomjs', os.path.join(os.path.dirname(__file__), 'phantom-capture-script.js'), url, fileNamePath], stdout=PIPE, stderr=STDOUT)
        external_process.communicate()

    print os.getcwd()
    print os.path.dirname(__file__)
    return_file = open(fileNamePath, 'rb')
    response = HttpResponse(return_file.read(), mimetype='image/png')
    #response['Content-Disposition'] = 'attachment; filename=image.png'
    return response
