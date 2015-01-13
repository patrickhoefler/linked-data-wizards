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

class D3DataGenerator(object):
    mappingInfoDimension = None
    mappingInfoMeasure = None
    dimensions = None
    labelOfDimensionArray = []
    labelOfMeasureArray = []
    results = {'code': '', 'errors': []}

    def __init__(self, mappingInfoForDimension, mappingInfoForMeasure, mappingInfoForValue):
        self.mappingInfoDimension = mappingInfoForDimension


        self.mappingInfoMeasure = mappingInfoForMeasure
        self.mappingInfoValue = mappingInfoForValue

    def transform(self):

        try:

            self.results = {'code': '', 'errors': [], 'id': ''}
            rows = []
            columns = self.transformColumns()

            for element in self.mappingInfoValue:
                rowValues = []
                for i in range(len(self.mappingInfoDimension)):
                    rowValues.append(element['observation']['dimensionlabel' + str(i)])
                for i in range(len(self.mappingInfoMeasure)):
                    rowValues.append(element['observation']['measurevalue' + str(i)])
                rows.append(rowValues)

            self.results["columns"] = columns
            self.results["rows"] = rows

        except Exception as ex:
            raise Exception("-D3DataGenerator.transform: %s" % ex)

    def transformColumns(self):

        try:
            columns = []
            for element in self.mappingInfoDimension:
                dimension = element['label']
                columns.append(dimension)

            for element in self.mappingInfoMeasure:
                measure = element['label']
                columns.append(measure)

            return columns

        except Exception as ex:
            raise Exception("-D3DataGenerator.transformColumns: %s" % ex)
