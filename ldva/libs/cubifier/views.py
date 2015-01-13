# encoding: utf-8
"""Views for the Cubifier."""

from __future__ import unicode_literals
from django.http import HttpResponse
from ldva.libs.cubifier.cubegen import create_and_save_cube


def test(request):
    response = create_and_save_cube(None)
    return HttpResponse(response)
