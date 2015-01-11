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

from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib
from django.conf import settings
import os

g=rdflib.Graph()
g.load(os.path.join(os.path.dirname(__file__), 'static/data/chart.rdf'))

  
q="""
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
prefix xs: <http://www.w3.org/2001/XMLSchema#> 
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix code: <http://code-research.eu/ontology/visual-analytics>
prefix sio: <http://semanticscience.org/ontology/sio.owl> 
prefix va: <http://code-research.eu/ontology/visual-analytics#> 


SELECT distinct  ?name ?vis ?datatype ?persistence ?supportedtype
WHERE { ?x va:hasChartName ?chart.
        ?x rdfs:label ?name.
        ?x va:hasVisualChannel ?vis.
        ?vis rdfs:label ?visualchannel.
        ?vis va:hasDataType ?datatype.
        ?vis va:hasPersistence ?persistence.
        ?vis va:supportsType ?supportedtype
     
      }
"""


for x in g.query(q):

    """print x[0]
    print x[1]
    print x[2]
    print x[3]
    print x[4]"""