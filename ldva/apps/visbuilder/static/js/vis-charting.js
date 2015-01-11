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

var brushingObserver = {
    listenersChartRowIndexMapping: [],
    listeners: [],
    registerListener : function(callbackUpdateChartRowIndex, chartRowIndex, callbackData, callbackDimensions){
        var listenerObject = { };
        var didAlreadyExist = false;
        for(var i=0; i<brushingObserver.listeners.length; i++){
            if (brushingObserver.listeners[i].chartRowIndex == chartRowIndex){
                listenerObject = brushingObserver.listeners[i];
                didAlreadyExist = true;
            }
        }
        listenerObject.callbackUpdateChartRowIndex = callbackUpdateChartRowIndex;
        listenerObject.callbackData = callbackData;
        listenerObject.callbackDimensions = callbackDimensions;
        listenerObject.chartRowIndex = chartRowIndex;

        if (!didAlreadyExist)
            brushingObserver.listeners.push(listenerObject);
        //if (!listenerObject.callbackUpdateChartRowIndex)
        //    throw Error('Callback "callbackUpdateChartRowIndex" is missing!!');
    },
    unregister : function(chartRowIndex){
        var newListeners = [];
        _.each(brushingObserver.listeners, function(item, i){
            if (item.chartRowIndex != chartRowIndex){
                newListeners.push(item);
                if (item.chartRowIndex > chartRowIndex){
                    item.chartRowIndex = item.chartRowIndex-1;
                    item.callbackUpdateChartRowIndex(item.chartRowIndex);
                }
            }
        });
        brushingObserver.listeners = newListeners;
    },
    lastSelectedData:null,
    lastSelectedDimensions:null,
    update: function(originChartRowIndex, selectedData, selectedDimensions){
        //console.log('Brushing update...');
        var originDatasetIndex = Vis.view.chartRows[originChartRowIndex].datasetIndex;
        //console.log(selectedData);
        if (selectedData == undefined || selectedData.length == 0)
            selectedData = null;
        if (selectedDimensions != undefined && selectedDimensions.length == 0)
            selectedDimensions = null;
        selectedDimensions = charting.convertSelectedDataToSelectedDimensions(getChannelMappingForViz(originChartRowIndex), selectedData, selectedDimensions);
        var selectedDataChanged = !_.isEqual(selectedData, brushingObserver.lastSelectedData);
        var selectedDimensionsChanged = !_.isEqual(selectedDimensions, brushingObserver.lastSelectedDimensions);
        brushingObserver.lastOriginDatasetIndex = originDatasetIndex;
        brushingObserver.lastSelectedData = _.map(selectedData, function (item){ return item});
        brushingObserver.lastSelectedDimensions = _.map(selectedDimensions, function (item){ return item});
        //console.log('selectedDimensionsChanged: ' + selectedDimensionsChanged);
        //console.log('selectedDimensions !== undefined: ' + (selectedDimensions !== undefined));
        //console.log('selectedDimensions: ');
        //console.log(selectedDimensions);
        for(var i=0; i<brushingObserver.listeners.length; i++){
            if (brushingObserver.listeners[i].chartRowIndex != originChartRowIndex){
                if (Vis.view.chartRows[brushingObserver.listeners[i].chartRowIndex].datasetIndex == originDatasetIndex && selectedDataChanged){
                    brushingObserver.listeners[i].callbackData(selectedData);
                } else if (brushingObserver.listeners[i].callbackDimensions && selectedDimensions !== undefined && selectedDimensionsChanged) {
                    brushingObserver.listeners[i].callbackDimensions(selectedDimensions);
                }
            }
        }
    },
    initializeSelfUpdate: function(selfChartRowIndex){
        var selectedData = brushingObserver.lastSelectedData;
        var selectedDimensions = brushingObserver.lastSelectedDimensions;
        if (selectedData == undefined || selectedData.length == 0)
            selectedData = null;
        if (selectedDimensions != undefined && selectedDimensions.length == 0)
            selectedDimensions = null;
        for(var i=0; i<brushingObserver.listeners.length; i++){
            if (brushingObserver.listeners[i].chartRowIndex == selfChartRowIndex){
                if (Vis.view.chartRows[brushingObserver.listeners[i].chartRowIndex].datasetIndex == brushingObserver.lastOriginDatasetIndex){
                    brushingObserver.listeners[i].callbackData(selectedData);
                } else if (brushingObserver.listeners[i].callbackDimensions && selectedDimensions !== undefined) {
                    brushingObserver.listeners[i].callbackDimensions(selectedDimensions);
                }
            }
        }
    },
    updateEmpty: function(originChartRowIndex){
        brushingObserver.update(originChartRowIndex, null, null);
    }
};


var charting = {

    getChannelMappingForChannel: function(channelMappings, channel){
        for(var j= 0, max=channelMappings.length; j<max; j++){
            if (channelMappings[j].channel == channel){
                return channelMappings[j];
            }
        }
        return null;
    },

    getDimensionByUri: function(dimensions, uri){
        for(var j= 0, max=dimensions.length; j<max; j++){
            if (dimensions[j].uri == uri){
                return dimensions[j];
            }
        }
        return null;
    },

    getRawDataFromVisObject: function(visObject, channelMappings){
        var returnDataRow = [];
        for(var j= 0, max=channelMappings.length; j<max; j++){
            if (channelMappings[j].channel == 'x-Axis'){
                returnDataRow[j] = visObject.xAxis;
            } else if (channelMappings[j].channel == 'y-Axis'){
                returnDataRow[j] = visObject.yAxis;
            } else if (channelMappings[j].channel == 'Color'){
                returnDataRow[j] = visObject.bubbleColor;
            } else if (channelMappings[j].channel == 'Size'){
                returnDataRow[j] = visObject.bubbleSize;
            }
        }

        return returnDataRow;
    },

    setSelectedProperty: function(visObjects, selectedData, channelMappings){
        visObjects.each(function(visObject) {
            if (visObject) {
                var rawData = charting.getRawDataFromVisObject(visObject, channelMappings);
                visObject.selected = false;
                for(var i= 0, max=selectedData.length; i<max; i++){
                    if (selectedData[i].compare(rawData))
                        visObject.selected = true;
                }
            }
        });
    },

    convertSelectedDataToSelectedDimensions: function(channelMapping, selectedData, selectedDimensions){
        if (selectedData == null)
            return null;
        if (selectedDimensions == null)
            selectedDimensions = [];

        for(var i=0; i<channelMapping.length; i++){
            if (channelMapping[i].datatype == "string"){
                var selectedDimension = charting.getDimensionByUri(selectedDimensions, channelMapping[i].uri);

                // start mapping:
                var selectedValues = [];
                for(var j=0; j<selectedData.length; j++){
                    var currentData = selectedData[j][i];
                    if (!_.contains(selectedValues, currentData)){
                        selectedValues.push(currentData);
                    }
                }
                if (selectedDimension == null){
                    var dimensionNew = {
                        from: null,
                        to: null,
                        uri: channelMapping[i].uri,
                        label: channelMapping[i].label,
                        type: channelMapping[i].type,
                        values: selectedValues
                    };
                    selectedDimensions.push(dimensionNew);
                } else {
                    selectedDimension.values = selectedValues;
                }
            }
        }

        return selectedDimensions;
    }

};