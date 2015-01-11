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


@csrf_exempt # Ohne das funktioniert post nicht
def service(request):
    
    cmd = ""
    if request.method == 'GET':
        cmd=request.GET['cmd']
    else:
        cmd=request.POST['cmd']
    
    mappingProposalObject = mappingproposal.MappingProposal()

    response = HttpResponse()
    
    if(cmd=="getPreview"):
        try:
            ds=request.POST['dataset']
            chart=request.POST['chart']
            chartID=request.POST['chartid']
            
            inProcessorObject=inprocessor.InProcessor(ds, chart, chartID)
            inProcessorObject.process()
            resultArray=inProcessorObject.resultArray
        
            return HttpResponse(json.dumps(resultArray))
            
        except Exception as inst:
            msg = "ERROR (code - queryPreview): [%s] %s"%(type(inst),inst)
            
            print msg
            mappingProposalObject.reInit()
        
            return HttpResponse(json.dumps({'error' : ''+msg+''}))

   
    if(cmd=="getPreviewAuto"):
        try:
            ds=request.POST['dataset']
            chart=request.POST['chart']
            dimension= request.POST['dimension'] 
            resultArray = []
            
            inProcessorObject=inprocessorauto.InProcessorAuto(ds, chart, dimension )
            resultArray = inProcessorObject.process()
        
            '''for i in range(len(resultArray)):
                supChart = resultArray[i]['chart']
                supChartUri = resultArray[i]['charturi']
                chartArray.append(supChart)'''
            
            #print "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK", resultArray
            
            return HttpResponse(json.dumps(resultArray))
            
            
        except Exception as inst:
            msg = "ERROR (code - queryPreviewAuto): [%s] %s"%(type(inst),inst)
            
            print msg
            #mappingProposalObject.reInit()
        
            return HttpResponse(json.dumps({'error' : ''+msg+''}))
    
    if(cmd=="getVisualization"):
        try:
            dimUriArray = []
            ds=request.POST['dataset']
            chart=request.POST['chart']
            dimension= json.loads(request.POST['dimension'])
            #print "HIERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRr", dimension
            dimUri = ""
            
            for elements in dimension:
                dimUri = elements['dimensionuri']
                dim = elements ['dim']
                dimUriObject = {'dimensionuri':dimUri, 'dim': dim }
                dimUriArray.append(dimUriObject)
            
            inProcessorObject=inprocessorauto.InProcessorAuto(ds, chart, dimUriArray)
            resultArray = inProcessorObject.getVis()
            #resultArray=inProcessorObject.resultArray
        
            return HttpResponse(json.dumps(resultArray))
            
        except Exception as inst:
            msg = "ERROR (code - queryVisualization): [%s] %s"%(type(inst),inst)
            
            print msg
            mappingProposalObject.reInit()
        
            return HttpResponse(json.dumps({'error' : ''+msg+''}))
        
    
    if(cmd=="getDimension"):
        try:
            ds=request.POST['dataset']
         
            sparqlqueryObjectD3 = ""
            
            if ds == "http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3":
                sparqlqueryObjectD3=SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')
            else:
                sparqlqueryObjectD3=SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')   
                    
            dimensions=sparqlqueryObjectD3.get_cube_dimensions_for_auto_mapping(ds)  

            return HttpResponse(json.dumps(dimensions))
            
        except Exception as inst:
            msg = "ERROR (code - getDimension): [%s] %s"%(type(inst),inst)
            
            print msg
            mappingProposalObject.reInit()
        
            return HttpResponse(json.dumps({'error' : ''+msg+''}))


    if(cmd=="getMeasure"):
        try:
            ds = request.POST['dataset']
         
            sparqlqueryObjectD3 = ""
            
            if ds == "http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3":
                sparqlqueryObjectD3=SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')
            else:
                sparqlqueryObjectD3=SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')   
                    
            dimensions=sparqlqueryObjectD3.get_cube_measure_for_auto_mapping(ds)  
            #print "HIERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR", dimensions
            return HttpResponse(json.dumps(dimensions))
            
        except Exception as inst:
            msg = "ERROR (code - getMeasure): [%s] %s"%(type(inst),inst)
            
            print msg
            mappingProposalObject.reInit()
        
            return HttpResponse(json.dumps({'error' : ''+msg+''}))  
        

    if (cmd=="getD3Data"):
        try:
            #chart=request.GET['chart']
            
            chartID=request.GET['chartid']
            ds=request.GET['dataset']
            
            inProcessorObject=inprocessor.InProcessor(ds, "d3data", chartID)
            inProcessorObject.process()
            resultArray=inProcessorObject.resultArray

            return HttpResponse(json.dumps(resultArray))
            
        except Exception as ex:
            msg = "ERROR (code - getD3Data): [%s] %s"%(type(ex), ex)
            print msg
        
    
                  
