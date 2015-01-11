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

"""
Update the app from Git and restart it
"""
import os
import subprocess


def application(environ, start_response):
    """
    Pull the current version from the GitHub repository
    and touch wsgi.py to restart the app
    """
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)

    # Pull the current version
    process = subprocess.Popen(
        'git pull',
        shell=True,
        cwd=os.path.join(os.path.dirname(__file__), '..'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (stdoutdata, stderrdata) = process.communicate()
    output = stdoutdata + stderrdata

    # Collect the static files
    process = subprocess.Popen(
        'python manage.py collectstatic --noinput --clear',
        shell=True,
        cwd=os.path.join(os.path.dirname(__file__), '..'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (stdoutdata, stderrdata) = process.communicate()
    output += stdoutdata + stderrdata

    # Touch wsgi.py to trigger a restart
    process = subprocess.Popen(
        'touch ' + os.path.join(os.path.dirname(__file__), 'wsgi.py'),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (stdoutdata, stderrdata) = process.communicate()
    output += stdoutdata + stderrdata

    return output
