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

class InProcessor():
    selectedChart=""
    resultArray = []
    def __init__(self, ds, chart, chartID):
        self.dataset = ds
        self.selectedChart = chart
        self.iDOfSelectedChart = chartID
       
            
    def process(self):
        try:
            outProcessorObject = outprocessor.OutProcessor(self.dataset, self.selectedChart, self.iDOfSelectedChart)
            outProcessorObject.process()
            self.resultArray = outProcessorObject.resultArray
        except Exception as ex:
            raise Exception("-InProccessor.process: %s"%ex)
        
        
    