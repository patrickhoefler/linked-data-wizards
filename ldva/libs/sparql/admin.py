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

from __future__ import unicode_literals

"""
Admin interface for the SPARQL logs
"""

from django.contrib import admin
from ldva.libs.sparql.models import Endpoint, Dataset, Log


class EndpointAdmin(admin.ModelAdmin):
    """Modify the display of the endpoint list"""
    list_display = ('id', 'label', 'sparql_url', 'search_type', 'default_language', 'website_url', 'sort_order')

admin.site.register(Endpoint, EndpointAdmin)


class DatasetAdmin(admin.ModelAdmin):
    """Modify the display of the dataset list"""
    list_display = ('endpoint', 'uri', 'label', 'description', 'size', 'updated')

admin.site.register(Dataset, DatasetAdmin)


class LogAdmin(admin.ModelAdmin):
    """Modify the display of the SPARQL logs"""
    list_display = ('date_time', 'type', 'runtime', 'result_count', 'endpoint')

admin.site.register(Log, LogAdmin)
