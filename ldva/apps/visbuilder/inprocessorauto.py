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

import outprocessor
import outprocessorauto
import time


class InProcessorAuto():
    def __init__(self, ds, chart, dimension, endpoint, deletedMeasure, chartrowindex, datasetFilters ):
        self.dataset = ds
        self.selectedChart = chart
        self.dimension = dimension

        self.endpoint = endpoint
        self.deletedMeasure = deletedMeasure
        self.chartrowindex = chartrowindex
        self.datasetFilters = datasetFilters


    def process(self):
        try:
            time_start = time.time()

            outProcessorForAuto = outprocessorauto.OutProcessorForAutomaticallyMapping(self.dataset, self.selectedChart, self.dimension, self.endpoint, self.deletedMeasure, self.chartrowindex, self.datasetFilters )
            resultArray = outProcessorForAuto.process()
            time_end = time.time() - time_start
            return resultArray

        except Exception as ex:
            print ("-InProccessorAuto.process: %s"%ex)
            raise Exception("%s"%ex)

    def getVis(self):
        try:
            outProcessorForAuto = outprocessorauto.OutProcessorForAutomaticallyMapping(self.dataset, self.selectedChart, self.dimension, self.endpoint, self.deletedMeasure, self.chartrowindex, self.datasetFilters)
            resultArray = outProcessorForAuto.getVis()
            return resultArray
        except Exception as ex:
            raise Exception("-InProccessorAuto.getVis: %s"%ex)

