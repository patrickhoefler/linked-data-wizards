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

import json
import mappingproposal
import inprocessor
import inprocessorauto
import parallelcoordinatesgenerator
import d3data



from ldva.libs.sparql.utils import SPARQLQuery
from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from ldva.libs.sparql.models import Endpoint


@csrf_exempt # post does not work without them
def service(request):
    
    cmd = ""
    if request.method == 'GET':
        cmd=request.GET['cmd']
    else:
        cmd=request.POST['cmd']
    
    mappingProposalObject = mappingproposal.MappingProposal()

    response = HttpResponse()
    mappingCombi = []
    groupedBy = []
  

   
    if(cmd=="getPreviewAuto"):
        try:
            resultArray = []
            deletedMeasure = []
            ds = request.POST['dataset']
            chart = request.POST['chart']
            
            dimension = request.POST['dimension'] 
            endpoint = request.POST['endpoint']
            deletedMeasure = json.loads(request.POST['deletedmeasures']) 
            chartRowIndex = request.POST['chartrowindex']
            datasetFilters = json.loads(request.POST['datasetFilters'])
            
            
            
            resultArray = []
            inProcessorObject = inprocessorauto.InProcessorAuto(ds, chart, dimension, endpoint, deletedMeasure, chartRowIndex, datasetFilters)
            resultArray = inProcessorObject.process()
  
           
            response = HttpResponse()
            response.content = json.dumps(resultArray)
            response['Access-Control-Allow-Origin']="*"
            response['Access-Control-Allow-Methods']="POST, GET, OPTIONS"
            response['Access-Control-Allow-Headers']="*"
            
            return response
            
            
        except Exception as inst:
            msg = "ERROR (code - queryPreviewAuto): [%s] %s"%(type(inst),inst)
            msg2 = "%s"%(inst)
            print msg
            
            return HttpResponse(json.dumps({'error' : ''+msg2+''}))
    
    if(cmd=="getVisualization"):
        try:
            datasetFilters = []
            resultArray = []
            dimUriArray = []
            ds=request.POST['dataset']
            
            chart = request.POST['chart']
            dimension = json.loads(request.POST['dimension'])
            endpoint = request.POST['endpoint']
            
            deletedMeasure = json.loads(request.POST['deletedmeasures'])
            chartRowIndex = request.POST['chartrowindex']
            datasetFilters = json.loads(request.POST['datasetFilters'])
            
          
            
            
            
            dimUri = ""
        
            for elements in dimension:
                dimUri = elements['dimensionuri']
                dim = elements ['label']
                
                cubeComponent = elements['cubecomponent']
                index = elements['index']
                
                
                dimUriObject = {'dimensionuri':dimUri, 'label': dim, 'cubecomponent':cubeComponent , 'index':index}
                dimUriArray.append(dimUriObject)
               
            inProcessorObject=inprocessorauto.InProcessorAuto(ds, chart, dimUriArray, endpoint, deletedMeasure, chartRowIndex, datasetFilters )
            resultArray = inProcessorObject.getVis()
            return HttpResponse(json.dumps(resultArray))
            
        except Exception as inst:
            msg = "ERROR (code - queryVisualization): [%s] %s"%(type(inst),inst)
            msg2 = "%s"%(inst)
            print msg
            
            return HttpResponse(json.dumps({'error' : ''+msg2+''}))
        
    
    if(cmd=="getDimension"):
        try:
            ds = request.POST['dataset']
            endpoint = request.POST['endpoint']
            sparqlqueryObjectD3 = ""
            
            ''' st = "http://data.lod2.eu/"   
            if st in ds:    
                sparqlqueryObjectD3=SPARQLQuery('http://open-data.europa.eu/en/sparqlep', 'regex')
            else:
                sparqlqueryObjectD3=SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso') '''

            if not endpoint:
                endpoint = \
                    'http://zaire.dimis.fim.uni-passau.de:8890/sparql'

            search_type = 'regex'

            sparqlqueryObjectD3 = SPARQLQuery(endpoint, search_type)

            dimensions = sparqlqueryObjectD3.get_cube_dimensions_for_auto_mapping(ds)  
            
            return HttpResponse(json.dumps(dimensions))
            
        except Exception as inst:
            msg = "ERROR (code - getDimension): [%s] %s"%(type(inst),inst)
            
            print msg
            mappingProposalObject.reInit()
        
            return HttpResponse(json.dumps({'error' : ''+msg+''}))


    if(cmd=="getMeasure"):
        try:
            ds = request.POST['dataset']
            endpoint = request.POST['endpoint']
            deletedMes = json.loads(request.POST['deletedmeasures'])
            sparqlqueryObjectD3 = ""        
            '''st = "http://data.lod2.eu/"    
            
            if st in ds:    
                sparqlqueryObjectD3=SPARQLQuery('http://open-data.europa.eu/en/sparqlep', 'regex')
            else:
                sparqlqueryObjectD3=SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')'''
            
            if not endpoint:
                endpoint = \
                    'http://zaire.dimis.fim.uni-passau.de:8890/sparql'

            search_type = 'regex'

            sparqlqueryObjectD3 = SPARQLQuery(endpoint, search_type)
                    
            measures = sparqlqueryObjectD3.get_cube_measure_for_auto_mapping(ds, deletedMes)  
        
            return HttpResponse(json.dumps(measures))
            
        except Exception as inst:
            msg = "ERROR (code - getMeasure): [%s] %s"%(type(inst),inst)
            print msg
        
            return HttpResponse(json.dumps({'error' : ''+msg+''}))  
        

    if (cmd=="getD3Data"):
        try: 
            chartID=request.GET['chartid']
            ds=request.GET['dataset']
            
            inProcessorObject=inprocessor.InProcessor(ds, "d3data", chartID)
            inProcessorObject.process()
            resultArray=inProcessorObject.resultArray

            return HttpResponse(json.dumps(resultArray))
            
        except Exception as ex:
            msg = "ERROR (code - getD3Data): [%s] %s"%(type(ex), ex)
            print msg
            return HttpResponse(json.dumps({'error' : ''+msg+''})) 
        
    if(cmd=="getChartSVG"):
        try:
            chartName=request.GET['chartname']
           
            svgImage = mappingProposalObject.getChartSVG( chartName )
            return HttpResponse(svgImage)
            
        except Exception as inst:
            msg = "ERROR (code - getChartSVG): [%s] %s"%(type(inst),inst)          
            print msg        
            return HttpResponse(json.dumps({'error' : ''+msg+''}))

     
    
   
        
    

        
        