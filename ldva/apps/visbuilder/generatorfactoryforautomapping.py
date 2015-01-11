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

import barchartgenerator
import columnchartgenerator
import parallelgenerator
import piechartgenerator
import streamgraphgenerator
import groupedbarchartgenerator
import scatterplotmatrixgenerator
import geovisgenerator
import tablegenerator
import d3data


class GeneratorFactoryForAutoMapping():
    
    def __init__(self):
        pass
    
    def createFactoryauto(self, name, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue, dataset, chartrowIndex):
        try:
            if name=="parallelcoordinates":
                parallelCoordinatesGenerator= parallelgenerator.ParallelGenerator(mappingInfoForDimension, mappingIngfoForMeasure,  mappingInfoForValue, dataset, chartrowIndex)
                return(parallelCoordinatesGenerator)
            
            if name=="piechart":
                pieChartGenerator= piechartgenerator.PieChartGenerator(mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue, dataset, chartrowIndex)
                return(pieChartGenerator)
            
            
            if name=="streamgraph":
                #print "OKAYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYyyyy"
                streamgraphGenerator= streamgraphgenerator.StreamgraphGenerator(mappingInfoForDimension, mappingIngfoForMeasure,  mappingInfoForValue, dataset, chartrowIndex)
                return(streamgraphGenerator)
            
            
            if name=="groupedbarchart":
                groupedChartGenerator= groupedbarchartgenerator.GroupedBarChartGenerator(mappingInfoForDimension, mappingIngfoForMeasure,  mappingInfoForValue, chartrowIndex)
                return(groupedChartGenerator)
            
            if name=="scatterplotmatrix":
                scatterplotmatrixGenerator = scatterplotmatrixgenerator.ScatterPlotMatrixGenerator(mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue)
                return(scatterplotmatrixGenerator)
            
            if name=="map":
                geovisGenerator = geovisgenerator.GeovisGenerator(mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue)
                return(geovisGenerator)
            
            if name=="table":
                tableGenerator = tablegenerator.TableGenerator(mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue)
                return(tableGenerator) 
            
            
            
            if name=="bubblechart" or name=="linechart" or name=="json" or name=="barchart":
                generator = d3data.D3DataGenerator(mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue)
                return(generator)
            
              
            else:
                print("WARNING: generator for %s does not exist" %name)
                return(None)
            
        except Exception as ex:
            raise Exception("-Generatorfactory.init: %s"%ex)