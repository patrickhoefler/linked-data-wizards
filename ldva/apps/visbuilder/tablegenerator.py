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

import generator
import rdflib
import math
import unicodedata

from ldva.libs.sparql.utils import SPARQLQuery
from django.utils import simplejson

class TableGenerator(generator.Generator):
    mappingInfoDimension = None
    mappingInfoMeasure = None
    dimensions = None

    labelOfDimensionArray = []
    labelOfMeasureArray = []
    measureContentArray = []
    codeObject = {'code': """ var chartRowIndex = null; var loc=config.location;$(document).ready(function() {
        $("#"+loc).html('<table cellpadding="0" cellspacing="0" border="0" class="display" id="example'+loc+'"></table>' );
        $('#example'+loc).dataTable( { "oLanguage": { "oPaginate": { "sNext": "", "sPrevious": "" } }, @@@DATA@@@  } );
        $("#"+loc).find('.display').before('<br />');
        $("#"+loc).parents('.vis').css('overflow','auto');
        chartRowIndex = $("#"+loc).parents('.vis-row').data('chartRowIndex');
        table(null, channelMappings, '#'+loc, chartRowIndex, '#example'+loc);
    });
 """}


    results={'code':'', 'errors':''}

    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue):

        self.mappingInfoDimension = mappingInfoForDimension
        self.mappingInfoMeasure = mappingIngfoForMeasure
        self.mappingInfoValue = mappingInfoForValue
        self.results = {'code':'', 'errors': ''}

    def transform(self):
        try:
            self.results =  {}
            lineArraytwo = []
            labOfdm = ""

            tableForDim = {}
            xEntries = []
            tableForDimArray= []


            for entry in self.mappingInfoDimension:
                dim = entry['dimensionuri']
                dimLabel = entry['label']
                tableForDim = {'dimension' : '', 'label': ''}

                tableForDim['dimension'] = dim
                tableForDim['label'] = dimLabel
                tableForDimArray.append(tableForDim)



            tableForMesArray = []
            for meas in self.mappingInfoMeasure:
                value = meas ['measureuri']
                label = meas ['label']
                tableForMeasure = {'measure' : '', 'label': ''}
                tableForMeasure ['measure'] = value
                tableForMeasure ['label'] = label

                tableForMesArray.append (tableForMeasure)

            strgLabel = '"aoColumns":['
            strResult = '"aaData":[ '

            xAxisArray = []
            for element in self.mappingInfoValue:
                    strg = ""
                    labelForDimension = ""
                    strg3 = ""
                    for i in range(len(tableForDimArray)):
                        xAxis = element['observation']['dimensionlabel%s'% (i)]
                        labelDim = tableForDimArray[i]['label']
                        labelForDimension = labelForDimension + ' {"sTitle":"' + labelDim + '"},'

                        strg = strg + '"'+xAxis+'",'
                        strg2 = ""
                        labelForValue = ""

                        for value in range(len(tableForMesArray)):
                            yAxis = element['observation']['measurevalue%s'%(value)]
                            labelValue = tableForMesArray[value]['label']
                            if not yAxis:
                                yAxis = str(0.0)


                            bol = self.isReal(yAxis)

                            if not bol:
                                yAxis = str(0.0)


                            strg2 = strg2 +yAxis+','
                            labelForValue =  labelForValue + '{"sTitle":"' + labelValue + '"},'

                        tempStrg5List = list(labelForValue)
                        tempStrg5List[len(tempStrg5List)-1]=""
                        labelForValue = "".join(tempStrg5List)



                    strg3 = strg+ strg2

                    tempStrg3List = list(strg3)
                    tempStrg3List[len(tempStrg3List)-1]=""
                    strg3 = "".join(tempStrg3List)



                    strValueObject = "[" +strg3+ "], "
                    tempStrg4List = list(strValueObject)
                    tempStrg4List[len(tempStrg4List)-1]=""
                    strValueObject = "".join(tempStrg4List)



                    toDictObject = strValueObject
                    strResult = strResult + toDictObject


            strgLabel = strgLabel+labelForDimension + labelForValue




            tempList = list(strResult)
            tempList[len(tempList)-1]=""
            strEndResult = "".join(tempList)

            strResult = strEndResult + "],"+ strgLabel   + "]"

            code=self.codeObject['code']
            code = code.replace("@@@DATA@@@", strResult)
            self.results['code'] = code

        except Exception as ex:
            raise Exception("-TableGenerator.transform: %s"%ex)

    def isReal(self, txt):
        try:
            float(txt)
            return True
        except ValueError:
            return False

