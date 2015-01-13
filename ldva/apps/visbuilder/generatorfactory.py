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

import parallelcoordinatesgenerator
import streamgraphgenerator
import d3piechartgenerator
import groupedbarchartgenerator
import d3data



class GeneratorFactory():

    def __init__(self):
        pass

    def createFactory(self, name, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue, possibleVisualizations):
        try:

            if name=="parallelcoordinates":
                parallelCoordinatesGenerator= parallelcoordinatesgenerator.ParallelCoordinatesGenerator(mappingInfoForDimension, mappingIngfoForMeasure,  mappingInfoForValue)
                return(parallelCoordinatesGenerator)

            if name=="streamgraph":
                streamgraphGenerator= streamgraphgenerator.StreamgraphGenerator(mappingInfoForDimension, mappingIngfoForMeasure,  mappingInfoForValue)
                return(streamgraphGenerator)

            if name=="piechart":
                pieChartGenerator= d3piechartgenerator.D3PieChartGenerator(mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue)
                return(pieChartGenerator)

            if name=="groupedbarchart":
                groupedChartGenerator= groupedbarchartgenerator.GroupedBarChartGenerator(mappingInfoForDimension, mappingIngfoForMeasure,  mappingInfoForValue)
                return(groupedChartGenerator)


            if name=="d3data":
                d3dataGenerator = d3data.D3DataGenerator(mappingInfoForDimension, mappingIngfoForMeasure,  mappingInfoForValue)
                return(d3dataGenerator)

            else:
                print("WARNING: generator for %s does not exist" %name)
                return(None)

        except Exception as ex:
            raise Exception("-Generatorfactory.init: %s"%ex)
