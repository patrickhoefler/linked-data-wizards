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

"""The models for our SPARQL helper."""

from django.db import models


class Endpoint(models.Model):

    """The list of supported endpoints."""

    id = models.CharField(primary_key=True, max_length=64)
    label = models.CharField(max_length=128)
    sparql_url = models.CharField('SPARQL URL', max_length=128)
    search_type = models.CharField(max_length=8, default='regex')
    default_language = models.CharField(max_length=2, default='en')
    website_url = models.CharField('Website URL', max_length=128)
    sort_order = models.PositiveSmallIntegerField(default=999)

    def __unicode__(self):
        return self.label

    class Meta:
        ordering = ['sort_order', 'label']


class Dataset(models.Model):

    """The list of datasets in all supported endpoints."""

    uri = models.CharField('URI', primary_key=True, max_length=255)
    endpoint = models.ForeignKey(Endpoint)
    label = models.CharField(max_length=256)
    description = models.TextField()
    size = models.PositiveIntegerField()
    updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.label

    class Meta:
        ordering = ['label']


class Log(models.Model):

    """A log for our SPARQL queries."""

    date_time = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=32)
    sparql_query = models.TextField('SPARQL query')
    runtime = models.DecimalField(max_digits=6, decimal_places=2)
    result_count = models.PositiveIntegerField()
    endpoint = models.CharField(max_length=256)

    def __unicode__(self):
        return str(self.date_time) + ' | ' + self.endpoint + ' | ' + self.type
