/*
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
*/

var table = function (datarows, channelMappings, targetSelector, chartRowIndex, tableSelector){


    var brushedData = [];
    var brushedDataFromOutside = null;
    var dataTable = $(tableSelector).dataTable();

    $.fn.dataTableExt.afnFiltering.push(
        function(oSettings, aData, iDataIndex) {
            if (brushedDataFromOutside == null)
                return true;

            for (var i=0; i<brushedDataFromOutside.length; i++){
                var dataDoesMatch = true;
                for (var j=0; j<channelMappings.length && dataDoesMatch; j++){
                    if (aData[j] != brushedDataFromOutside[i][j]){
                        dataDoesMatch = false;
                    }
                }
                if (dataDoesMatch){
                    return true;
                }
            }
            return false;
        }
    );


    brushingObserver.registerListener(function(newChartRowIndex){ chartRowIndex = newChartRowIndex; }, chartRowIndex, receiveBrushingUpdate);

    function receiveBrushingUpdate(selectedData){
        console.log('callback data changed... Table');
        brushedDataFromOutside = selectedData;
        if (brushedDataFromOutside == null){
            removeAllRowSelections();
        }
        dataTable.fnDraw();
    }
    function removeAllRowSelections(){
        var nodes = dataTable.fnGetNodes();
        for (var i=0 ; i<nodes.length ; i++) {
            $(nodes[i]).removeClass('row_selected');
        }
    }

    $(targetSelector + " tbody").on('click', 'tr', function(){
        $(this).toggleClass('row_selected');
        sendBrushingUpdate();
    });
    $(targetSelector + " input[type=text]").on('keyup', function(){
    //$(targetSelector).on('filter', function(e){
        console.log('filter');
        var brushedData = [];
        var selectedRows = dataTable.$('tr', {"filter": "applied"} );
        for(var i=0; i<selectedRows.length; i++){
            var dataRow = getDataArrayFromTr(selectedRows[i]);
            brushedData.push(dataRow);
        }
        brushingObserver.update(chartRowIndex, brushedData);
    });

    function sendBrushingUpdate(){
        var brushedData = [];
        var selectedRows = fnGetSelected(dataTable);
        for(var i=0; i<selectedRows.length; i++){
            var dataRow = getDataArrayFromTr(selectedRows[i]);
            brushedData.push(dataRow);
        }
        if (brushedData.length == 0){
            removeAllRowSelections();
            dataTable.fnDraw();
        }
        brushingObserver.update(chartRowIndex, brushedData);
    }

    function getDataArrayFromTr(row){
        var dataRow = [];
        $(row).find('td').each(function(i, val){
            var text = $(val).text();
            //console.log(i + ' = ' + text + '(' + channelMappings[i].datatype + ')');
            if (channelMappings[i].datatype == 'decimal')
                text = text*1;
            dataRow.push(text);
        });
        return dataRow;
    }

    function fnGetSelected(oTableLocal){
        return oTableLocal.$('tr.row_selected');
    }
    //function fnGetSelected(oTableLocal){
    //    var aReturn = new Array();
    //    var aTrs = oTableLocal.fnGetNodes();
    //    for ( var i=0 ; i<aTrs.length ; i++ ) {
    //        if ($(aTrs[i]).hasClass('row_selected')){
    //            aReturn.push( aTrs[i] );
    //        }
    //    }
    //    return aReturn;
    //}

    var drawVisualization = function(datarows) {
    };

    drawVisualization(datarows);
};