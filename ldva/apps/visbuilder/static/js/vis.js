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

// Vis.Charts
// Vis.Configuration
// Vis.Initializer
// Vis.Loading.
// Vis.navigation
// Vis.Ui
// Vis.Helper
if (!brushingObserver) brushingObserver = {};

//var Vis = Vis || { };
$(document).ready(function () { Vis.init()});


var Vis = {

    config : {
        debug : false,
        hideShowConfigSpeed : 400,
        isLoggedIntoFortytwo: (fortytwoId != '')
    },

    init : function(){
        // history
        //$.address.history(false); // start history not before the first chart was loaded
        Vis.view.chartRows.push(new Vis.view.ChartRow());
        Vis.data.datasets.push(new Vis.data.Dataset());
        $.address.change(Vis.navigation.addressChanged);
        initializeVisRow(0);
        $(document).on('show', '#screencast_modal', function() {
            $('#screencast_modal_body').html('<iframe width="853" height="480" src="http://www.youtube.com/embed/-WqI-uu6RNw" frameborder="0" allowfullscreen></iframe>');
        });
        $(document).on('hidden', '#screencast_modal', function() {
            $('#screencast_modal_body').html('');
        });
        $('#add-vis').on('click', function(){addNewVisualisation(0)});
        $('#add-vis-aggregate').on('click', function(){showAggregateModal(0)});
        $('#add-vis-dataset').on('click', function(){addNewDataset(0)});
        $('#dataset_endpoint_selector').on('change', getAndDisplayDatasetsOfSelectedEndpoint);
        $('#button-print').on('click', function(){
            Vis.view.showChartsOnly = true;
            Vis.navigation.updateAddress();
        });
        $('#button-capture').on('click', function(){
            var href = location.href.replace(Vis.navigation.paramNames.showChartsOnly + "=false","");
            location.href = "/phantom?url=" + encodeURIComponent(href + "&" + Vis.navigation.paramNames.showChartsOnly + "=true");
            Vis.view.loadingStarted();
        });
        $('#button-do').on('click', function(){
            var selectObjects = [["Toy Story 2", "Lee Unkrich", 90000000]];
            brushingObserver.update(-1, selectObjects);
        });
        var $dropdownMenuePullUps = $('.dropdown-menu.pull-top');
        $dropdownMenuePullUps.css('top', '-' + ($dropdownMenuePullUps.height() + 10) + 'px');
        $('#mindmeister-modal-link').on('click', function(e){
            e.preventDefault();
            showVisualisationsOnMindMap($('#mm_modal').modal());
        });
        $('#login').on('click', function(event){
            event.target.href += "?next=" + encodeURIComponent(window.location.pathname + window.location.search + window.location.hash);
        });
        $('a#querywizard').on('click', function(event){
            event.target.href = Vis.view.queryWizardUri ||  '/search#?dataset=' + Vis.data.datasets[0].uri + '&endpoint=' + Vis.data.datasets[0].endpoint;
        });
    },

    data : {
        datasets :[],
        Dataset : function(){
            this.uri = null;
            // todo: move deletedMeasures to 'Charts' --> means loading the DatasetMetadata need to be splited...
            this.deletedMeasures = [];
            this.dimensions = [];
            this.measures = [];
            this.receivedDataRows = null;
            this.charts = [];
            this.datasetName = null;
            this.isDirty = false;
        },

        getPredicateLabel : function (predicateUri) {
            var datasetIndex = 0;
            for (var i = 0, max = Vis.data.datasets[datasetIndex].dimensions.length;  i<max; i++) {
                if (Vis.data.datasets[datasetIndex].dimensions[i].dimensionuri == predicateUri)
                    return Vis.data.datasets[datasetIndex].dimensions[i].label;
            }
            for (i = 0, max = Vis.data.datasets[datasetIndex].measures.length;  i<max; i++) {
                if (Vis.data.datasets[datasetIndex].measures[i].measureuri == predicateUri)
                    return Vis.data.datasets[datasetIndex].measures[i].label;
            }
            return "";
        },

        removeDataset: function(datasetIndexToRemove){
            var newDatasets = [];
            var newChartRows = [];
            for(var i= 0, max=Vis.data.datasets.length; i<max; i++){
                if (datasetIndexToRemove == i)
                    continue;
                newDatasets.push(Vis.data.datasets[i]);
            }
            for(i=0, max=Vis.chartRows.length; i<max; i++){
                if (Vis.charts[i].datasetIndex != datasetIndexToRemove){
                    if (Vis.charts[i].datasetIndex > datasetIndexToRemove)
                        Vis.charts[i].datasetIndex = Vis.charts[i].datasetIndex-1;
                    newChartRows.push(Vis.charts[i]);
                }
            }
            Vis.data.datasets = newDatasets;
            Vis.view.chartRows = newChartRows;
            Vis.view.updateChartRowData();
        }
    },

    view : {
        // move to Vis.data?
        queryWizardPredicates : [],
        queryWizardUri : null,
        datasetFilters : [], // todo: move to dataset?
        chartIdCurrentlyEditing : 0,
        //receivedDataRows : null,
        showChartsOnly : null,
        zoom : 1,
        chartRows : [ ],
        ChartRow : function(datasetIndex){
            this.selectedChart = null;
            this.channelMappingChangedByHandStack = [];
            this.dimensionMapping = []; // {globals.chartRows[chartRowIndex].dimensionMapping[i].selectedChannel}
            this.measureMapping = [];
            this.isConfigMenuOpen = true;
            this.datasetIndex = (datasetIndex || 0) + 0;
            this.caption = null;
            //this.deletedMeasures = [];
        },
        isLoading : true,
        isConfigurationChanging : true,
        isLoadingCounter : 0,
        loadingFinishedCallback : null,
        loadingStarted: function () {
            Vis.view.isLoadingCounter++;
            if (Vis.view.isLoadingCounter == 1) {
                Vis.view.isLoading = true;
                $('#loadingindicator').show();
            }
        },
        loadingFinished: function () {
            Vis.view.isLoadingCounter--;
            if (Vis.view.isLoadingCounter == 0) {
                Vis.view.isLoading = false;
                $('#loadingindicator').hide();
                if (Vis.view.loadingFinishedCallback != null)
                    Vis.view.loadingFinishedCallback();
            }
            if (Vis.view.isLoadingCounter < 0)
                Vis.view.isLoadingCounter = 0;
        },
        setLoadingFinishedCallback: function (callback) {
            Vis.view.loadingFinishedCallback = callback;
        },

        getNewAxisLabel: function (oldLabel, callback) {
            $('#axis-label-input').val(oldLabel);
            $('#change-axis-label-save').off('click').on('click', function () {
                callback($('#axis-label-input').val());
                $('#change-axis-label-form').modal('hide');
            });
            $('#change-axis-label-form').modal();
        },

        showChartCaptionModal: function (chartRowIndex) {
            var $chartRow = $getVisRow(chartRowIndex);
            var oldCaption = $chartRow.find('h1').html();
            $('#chart-caption-input').val(oldCaption);
            $('#change-chart-caption-save').off('click').on('click', function () {
                var newCaption = $('#chart-caption-input').val();
                if (oldCaption != newCaption){
                    $chartRow.find('h1').html(newCaption);
                    Vis.view.chartRows[chartRowIndex].caption = newCaption;
                    $.address.parameter(Vis.navigation.paramNames.caption + chartRowIndex, newCaption)
                    $.address.update();
                }
                $('#change-chart-caption-form').modal('hide');
            });
            $('#change-chart-caption-form').modal();
        },

        displayFilterConfiguration : function () {
            var $filteringInfo = $('#filtering-info');
            $filteringInfo.find('ul').empty();
            var filterLength = Vis.view.datasetFilters.length;
            if (filterLength == 0){
                $filteringInfo.hide();
                return;
            }

            for(var i= 0; i<filterLength; i++){
                var filter = Vis.view.datasetFilters[i];
                $filteringInfo.find('ul').append($('<li><label>' + Vis.data.getPredicateLabel(filter.predicateUri) + ':</label> <span>' + filter.valueLabel + '</span></li>'));
            }
            $filteringInfo.show();
        },

        // Resets all Charts. for the given Dataset, just one Chart should be visible afterwards.
        resetMultipleCharts: function (datasetIndex){
            var firstDatasetUseFound = false;
            var chartRowsNew = [];

            for(var i= 0, max = Vis.view.chartRows.length; i<max; i++){
                if (Vis.view.chartRows[i].datasetIndex == datasetIndex){
                    if (firstDatasetUseFound){
                        // Delete
                        $getVisRow(i).not('.template').remove();
                        continue;
                    } else {
                        // Reset
                        firstDatasetUseFound = true;
                        chartRowsNew.push(Vis.configuration.getEmptyChartRow(datasetIndex));
                    }
                } else {
                    // Do nothing
                    chartRowsNew.push(Vis.view.chartRows[i]);
                }
            }
            Vis.view.chartRows = chartRowsNew;
        },

        updateChartRowData: function(){
            $('.vis-row').each(function(i){ $(this).attr('id', 'vis-row' + i).data('vis-row-index', i).data('chartRowIndex', i).data('datasetIndex', Vis.view.chartRows[i].datasetIndex).find('.vis-inner').attr('id', 'vis-inner' + i)});
        },

        setChartRowCaption: function(chartRowIndex, $newVisRow){
            if (Vis.view.chartRows[chartRowIndex].caption == null){
                Vis.configuration.setChartObjectCaption(chartRowIndex);
            }
            $newVisRow.find('h1').html(Vis.view.chartRows[chartRowIndex].caption);
        },

        applyZoom: function(){
            if (Vis.view.zoom == 1)
                $('html')
                    .css('-moz-transform','')
                    .css('-moz-transform-origin','')
                    .css('-o-transform','')
                    .css('-o-transform-origin','')
                    .css('-webkit-transform','')
                    .css('-webkit-transform-origin','');
            else
                $('html')
                    .css('-moz-transform','scale(' + Vis.view.zoom + ')')
                    .css('-moz-transform-origin','0 0')
                    .css('-o-transform','scale(' + Vis.view.zoom + ')')
                    .css('-o-transform-origin','0 0')
                    .css('-webkit-transform','scale(' + Vis.view.zoom + ')')
                    .css('-webkit-transform-origin','0 0');
        }
    }

    // for debug purposes
    //var fixedData = {"start": "", "rows": [["2007", "Belgium", "43874172"], ["2007", "Germany", "222188775"], ["2007", "Denmark", "12851468"], ["2007", "Greece", "47637348"], ["2007", "Spain", "63997903"], ["2007", "Finland", "31890005"], ["2007", "Croatia", "272270"], ["2007", "Ireland", "13730047"], ["2007", "Netherlands", "56208013"], ["2007", "Portugal", "15086035"], ["2007", "Turkey", "3496225"], ["2008", "Austria", "34738984"], ["2008", "Belgium", "37257391"], ["2008", "Cyprus", "3554784"], ["2008", "Estonia", "893007"], ["2008", "Greece", "38511294"], ["2008", "Spain", "50974614"], ["2008", "Hungary", "4762533"], ["2008", "Luxembourg", "2947310"], ["2008", "Latvia", "231784"], ["2008", "Malta", "58680"], ["2008", "Netherlands", "56624594"], ["2008", "Romania", "3139515"], ["2008", "Sweden", "38628294"], ["2008", "Slovak Republic", "690101"], ["2009", "Austria", "26126929"], ["2009", "Spain", "56533978"], ["2009", "Finland", "12678824"], ["2009", "Hungary", "3405345"], ["2009", "Ireland", "8213981"], ["2009", "Italy", "75886956"], ["2009", "Norway", "9208840"], ["2009", "Romania", "2268979"], ["2009", "United Kingdom", "74073790"], ["2010", "Czech Republic", "3206603"], ["2010", "Denmark", "15338576"], ["2010", "Spain", "89267213"], ["2010", "European Union - 27 countries", "1105232412"], ["2010", "Finland", "20214259"], ["2010", "Ireland", "32417727"], ["2010", "Romania", "3102308"], ["2010", "Slovak Republic", "1936616"], ["2010", "Turkey", "1801295"], ["2010", "United Kingdom", "144044396"], ["2011", "Greece", "46533773"], ["2011", "Croatia", "798447"], ["2011", "Iceland", "556320"], ["2011", "Poland", "5946324"], ["2011", "Portugal", "16918324"], ["2011", "Romania", "2205343"], ["2011", "Slovenia", "4005421"], ["2011", "Slovak Republic", "2432966"], ["2011", "United Kingdom", "124319605"], ["2007", "Bulgaria", "2211431"], ["2007", "Czech Republic", "7664670"], ["2007", "Estonia", "1306739"], ["2007", "European Union - 27 countries", "953641029"], ["2007", "Hungary", "5858492"], ["2007", "Latvia", "161318"], ["2007", "Slovak Republic", "1879190"], ["2007", "United Kingdom", "111991060"], ["2008", "Bulgaria", "2298593"], ["2008", "Czech Republic", "3839633"], ["2008", "Germany", "180642820"], ["2008", "Denmark", "11919724"], ["2008", "Finland", "23725586"], ["2008", "France", "94284321"], ["2008", "Croatia", "446110"], ["2008", "Iceland", "829222"], ["2008", "Lithuania", "312857"], ["2008", "Norway", "9264806"], ["2008", "Portugal", "13721754"], ["2009", "Bulgaria", "868748"], ["2009", "Cyprus", "3257139"], ["2009", "Czech Republic", "5941656"], ["2009", "Denmark", "11043078"], ["2009", "Estonia", "990917"], ["2009", "Greece", "27618968"], ["2009", "Croatia", "595192"], ["2009", "Iceland", "228192"], ["2009", "Latvia", "695460"], ["2009", "Netherlands", "48103515"], ["2009", "Sweden", "25029940"], ["2009", "Slovak Republic", "1861622"], ["2009", "Turkey", "2696691"], ["2010", "Austria", "37289527"], ["2010", "Germany", "276220811"], ["2010", "Estonia", "1605557"], ["2010", "Greece", "47000278"], ["2010", "France", "109799863"], ["2010", "Hungary", "9217427"], ["2010", "Italy", "129798025"], ["2010", "Lithuania", "815823"], ["2010", "Luxembourg", "253235"], ["2010", "Latvia", "548054"], ["2010", "Malta", "65741"], ["2010", "Netherlands", "57451491"], ["2010", "Portugal", "16420331"], ["2010", "Sweden", "39963912"], ["2010", "Slovenia", "6772867"], ["2011", "Belgium", "44285262"], ["2011", "Bulgaria", "1812279"], ["2011", "Cyprus", "2189469"], ["2011", "Czech Republic", "4590868"], ["2011", "Estonia", "409450"], ["2011", "Spain", "113484712"], ["2011", "Finland", "21900566"], ["2011", "France", "106333441"], ["2011", "Hungary", "4568167"], ["2011", "Ireland", "16621523"], ["2011", "Italy", "107816957"], ["2011", "Luxembourg", "4021125"], ["2011", "Latvia", "454354"], ["2011", "Malta", "241431"], ["2011", "Netherlands", "48695934"], ["2011", "Norway", "10553720"], ["2011", "Sweden", "30557448"], ["2011", "Turkey", "3744618"], ["2007", "Austria", "42635208"], ["2007", "Cyprus", "2636669"], ["2007", "France", "114567950"], ["2007", "Italy", "97448026"], ["2007", "Lithuania", "396514"], ["2007", "Luxembourg", "1550383"], ["2007", "Malta", "459599"], ["2007", "Norway", "10664210"], ["2007", "Poland", "6009467"], ["2007", "Romania", "5007213"], ["2007", "Sweden", "39404377"], ["2007", "Slovenia", "4988957"], ["2008", "European Union - 27 countries", "843141083"], ["2008", "Ireland", "10265438"], ["2008", "Italy", "95943223"], ["2008", "Poland", "9328450"], ["2008", "Slovenia", "4667587"], ["2008", "Turkey", "1828647"], ["2008", "United Kingdom", "119178212"], ["2009", "Belgium", "36749839"], ["2009", "Germany", "170480239"], ["2009", "European Union - 27 countries", "688679253"], ["2009", "France", "74130369"], ["2009", "Lithuania", "407040"], ["2009", "Luxembourg", "1093999"], ["2009", "Malta", "412342"], ["2009", "Poland", "8723461"], ["2009", "Portugal", "9824658"], ["2009", "Slovenia", "2257481"], ["2010", "Belgium", "47606752"], ["2010", "Bulgaria", "2380843"], ["2010", "Cyprus", "3202869"], ["2010", "Croatia", "194742"], ["2010", "Norway", "17165918"], ["2010", "Poland", "9291308"], ["2011", "Austria", "36527427"], ["2011", "Germany", "221015986"], ["2011", "Denmark", "10505245"], ["2011", "European Union - 27 countries", "978714002"], ["2011", "Lithuania", "320602"]], "name": "linechart", "columns": ["Year", "Country", "value"]};
    //var fixedMapping = [
    //    {channel: "Lines", datatype: "string", dimension: "Year"},
    //    {channel: "x-Axis", datatype: "string", dimension: "Country"},
    //    {channel: "y-Axis", datatype: "decimal", dimension: "Value"}];

};


Vis.navigation = {
    paramNames : {
        dataset : "dataset",
        datasetsPrefix : "ds",
        datasetsUri : "u",
        datasetsEndpoint : "e",
        datasetsDeletedMeasures : "dm",
        endpoint : "endpoint",
        selectedChart : "chart",
        datasetIndex : "chartDsIn",
        dimensionMapping : "dim",
        keyPart : "Key",
        valuePart : "Val",
        measureMapping : "ms",
        isConfigMenuOpen : "confOp",
        caption : "cap",
        emptyChartName : "empty",
        deletedMeasures : "measureDel",
        showChartsOnly : "chartsonly",
        zoom : "zoom",
        predicate : "p",
        predicateFilterType : "ft",
        predicateFilterValue : "fv",
        predicateFilterLabel : "fl"
    },

    addressChanged: function (event) {
        //console.log(event);

        if (event.parameters.userId && event.parameters.userId != fortytwoId){
            window.location.href ='/qa?userId=' + event.parameters.userId + '&callback=' + encodeURIComponent(window.location.href);
            return;
        }

        var newConfig = Vis.navigation.deserializeChartRowsConfig(event.parameters);
        newConfig.datasets = Vis.navigation.deserializeDatasets(event.parameters);

        Vis.view.showChartsOnly = newConfig.showChartsOnly;
        Vis.view.zoom = newConfig.zoom;
        var $body = $('body');
        if (Vis.view.showChartsOnly) {
            $body.addClass("charts-only");
            if (Vis.view.chartRows.length == 1) {
                $body.addClass("charts-only-single");
            }
        } else {
            $body.removeClass("charts-only").removeClass("charts-only-single");
        }
        Vis.view.applyZoom();

         // these parameters are coming from the Query Wiz
        Vis.view.queryWizardPredicates = Vis.navigation.deserializePredicates(event.parameters);
        Vis.view.datasetFilters = Vis.navigation.deserializeFilters(event.parameters);
        if (window.location.href.indexOf('?dataset=') >= 0) // "dataset" in the URL means, the url can be transformed to a querywizard url
            Vis.view.queryWizardUri = '/search#?' + window.location.href.slice(window.location.href.indexOf('?') + 1);

        // Clean the List of old Datasets:
        var datasets = [];
        for(var i=0; i< newConfig.datasets.length; i++){
            var newDs = newConfig.datasets[i];
            var existingDataset = _.find(Vis.data.datasets, function(oldDs){
                return oldDs.uri == newDs.uri;
            });
            if (existingDataset)
                datasets.push(existingDataset);
            else
                datasets.push(new Vis.data.Dataset());
        }
        Vis.data.datasets = datasets;

        Vis.navigation.addressChanged_CheckDatasetsChanged(newConfig);
    },

    addressChanged_CheckDatasetsChanged: function (newConfig, hasAnyDatasetChanged) {
        hasAnyDatasetChanged = hasAnyDatasetChanged || false;

        for(var i= 0, max=newConfig.datasets.length; i< max; i++){
            var datasetNew = newConfig.datasets[i];
            var datasetOld = Vis.data.datasets.length > i ? Vis.data.datasets[i] : new Vis.data.Dataset();

            if (datasetOld.isDirty || datasetNew.uri != datasetOld.uri || datasetNew.endpoint != datasetOld.endpoint || !datasetNew.deletedMeasures.compare(datasetOld.deletedMeasures)) {
                hasAnyDatasetChanged = true;
                datasetOld.isDirty = false;
                Vis.navigation.addressChanged_DatasetChanged(newConfig, datasetNew, i, function(){
                    Vis.navigation.addressChanged_CheckDatasetsChanged(newConfig, hasAnyDatasetChanged)
                });
                return;
            }
        }
        // delete datasets that are not found in the url:
        for(i=Vis.data.datasets.length-1; i>newConfig.length-1; i--){
            Vis.data.removeDataset(i);
        }

        //console.log('History before configure ChartRows: ' + $.address.history());
        //$.address.history(false);
        Vis.navigation.configureChartRows(newConfig);
    },

    addressChanged_DatasetChanged: function (newConfig, datasetNew, datasetIndex, callbackFinished) {
        // Dataset changed:
        Vis.data.datasets[datasetIndex].uri = datasetNew.uri;
        Vis.data.datasets[datasetIndex].endpoint = datasetNew.endpoint;
        Vis.data.datasets[datasetIndex].deletedMeasures = datasetNew.deletedMeasures;
        $('.vis-row[data-datasetIndex=' + datasetIndex + ']').find(".possiblecharts button").addClass('disabled').unbind('click');
        Vis.view.loadingStarted();
        Vis.loading.loadDatasetMetadata(datasetIndex, function (success, datasetIndex) {
            if (!success){
                // something bad happened when accessing base cube information... so what to do? act like there is nothing set...
                newConfig.datasets[datasetIndex].uri = "";
                newConfig.datasets[datasetIndex].endpoint = "";
                newConfig.datasets[datasetIndex].deletedMeasures = [];
                Vis.view.resetMultipleCharts(datasetIndex);
            }
            // if Dataset has successfully loaded metadata, go and reset dimensions and measures...
            for (var j = 0; j<newConfig.chartRows.length; j++){
                if (newConfig.chartRows[j].datasetIndex == datasetIndex){
                    var emptyChartRow = Vis.configuration.getEmptyChartRow(datasetIndex);
                    newConfig.chartRows[j].dimensionMapping = emptyChartRow.dimensionMapping;
                    newConfig.chartRows[j].measureMapping = emptyChartRow.measureMapping;
                }
            }
            Vis.view.loadingFinished();
            callbackFinished();
        });
    },

    configureChartRows: function (newConfig) {
        Vis.view.displayFilterConfiguration();

        if (newConfig.chartRows.length == 0) {
            if (newConfig.datasets.length == 0 || newConfig.datasets[0].uri == "" || newConfig.datasets[0].endpoint == "") {
                Vis.configuration.setChart(0, "");
                return;
            }
            return loadRandomChart(0);
        }
        Vis.view.isConfigurationChanging = true;
        for (var chartRowIndex = 0; chartRowIndex < newConfig.chartRows.length; chartRowIndex++) {
            var newChartRowConfig = newConfig.chartRows[chartRowIndex];
            var newChartName = "";

            if (Vis.view.chartRows.length < (chartRowIndex + 1)) {
                addNewVisualisation(newChartRowConfig.datasetIndex);
            }
            if (newChartRowConfig.selectedChart != null)
                newChartName = newChartRowConfig.selectedChart.chartname;

            if (Vis.view.chartRows[chartRowIndex].selectedChart != null) {
                var mappingIsOkay = isMappingValid(Vis.view.chartRows[chartRowIndex].selectedChart.possibleMappings, newChartRowConfig.dimensionMapping.concat(newChartRowConfig.measureMapping));
                if (mappingIsOkay) {
                    var mappingWasChanged = false;
                    for (var i = 0; i < newChartRowConfig.dimensionMapping.length; i++) {
                        mappingWasChanged |= setChannelForDimensionOrMeasure(chartRowIndex, newChartRowConfig.dimensionMapping[i].dimension, newChartRowConfig.dimensionMapping[i].selectedChannel);
                    }
                    for (i = 0; i < newChartRowConfig.measureMapping.length; i++) {
                        mappingWasChanged |= setChannelForDimensionOrMeasure(chartRowIndex, newChartRowConfig.measureMapping[i].dimension, newChartRowConfig.measureMapping[i].selectedChannel);
                    }
                    if (mappingWasChanged)
                        loadVisualization(chartRowIndex);
                }
            }

            if (newChartRowConfig.caption != Vis.view.chartRows[chartRowIndex].caption){
                Vis.view.setChartRowCaption(chartRowIndex, $getVisRow(chartRowIndex));
            }

            if (Vis.view.chartRows[chartRowIndex].selectedChart == null || Vis.view.chartRows[chartRowIndex].selectedChart.chartname != newChartName) {
                Vis.configuration.setChart(chartRowIndex, newChartName);
            }
        }

        for (; chartRowIndex < Vis.view.chartRows.length; chartRowIndex++) {
            removeChartRow(chartRowIndex);
        }

        // set all Id's correctly - as there was maybe a chart deleted:
        Vis.view.updateChartRowData();


        // open/close of chart Vis.configuration didn't work...
        //for(i=0; i<newConfig.chartRows.length; i++){
        //    if (newConfig.chartRows[i].isConfigMenuOpen)
        //        showChartConfiguration(i);
        //    else
        //        hideChartConfiguration(i);
        //}

        Vis.view.isConfigurationChanging = false;
    },

    deserializeFilters: function (parameters) {
        var predicates = Vis.navigation.deserializePredicates(parameters);
        var filters = [];
        for (var i=0, max=predicates.length; i<max; i++){
            var filterPredicatePrefix = Vis.navigation.paramNames.predicate + i;
            if (parameters[filterPredicatePrefix + Vis.navigation.paramNames.predicateFilterType]) {
                var filter = {
                    type : decodeURIComponent(parameters[filterPredicatePrefix + Vis.navigation.paramNames.predicateFilterType]),
                    value : decodeURIComponent(parameters[filterPredicatePrefix + Vis.navigation.paramNames.predicateFilterValue]),
                    valueLabel :  decodeURIComponent(parameters[filterPredicatePrefix + Vis.navigation.paramNames.predicateFilterLabel]),
                    predicateUri : predicates[i]
                };
                if (!filter.valueLabel || filter.valueLabel == 'undefined')
                    filter.valueLabel = filter.value;
                filters.push(filter);
            }
        }

        return filters;
    },

    deserializePredicates: function (parameters) {
        var predicates = [];
        var i = 0;
        while (parameters[Vis.navigation.paramNames.predicate + i]) {
            predicates.push(decodeURIComponent(parameters[Vis.navigation.paramNames.predicate + i]));
            i++;
        }
        return predicates;
    },

    deserializeChartRowsConfig: function (parameters) {
        var i, config = {
            chartRows : [],
            zoom : 1
        };
        var paramNames = Vis.navigation.paramNames;

        if (parameters[paramNames.dataset] == undefined && parameters[paramNames.datasetsPrefix + 0 + paramNames.datasetsUri] == undefined) {
            return config;
        }
        config.showChartsOnly = (parameters[paramNames.showChartsOnly] == "true");
        if (parameters[paramNames.zoom] != undefined)
            config.zoom = parameters[paramNames.zoom] * 1;

        i = 0;
        while (parameters[paramNames.selectedChart + i] != undefined) {
            var chartName = decodeURIComponent(parameters[paramNames.selectedChart + i]);
            var datasetIndex = (parameters[paramNames.datasetIndex + i] || 0) * 1;
            var chartRow = new Vis.view.ChartRow(datasetIndex);
            chartRow.isConfigMenuOpen = (parameters[paramNames.isConfigMenuOpen + i] == "true"); // todo: is this in use?
            if (parameters[paramNames.caption + i]){
                chartRow.caption = decodeURIComponent(parameters[paramNames.caption + i]);
            }

            if (chartName != paramNames.emptyChartName) {
                chartRow.selectedChart = { chartname: chartName };
            }
            var mapping, j = 0;
            while (parameters[paramNames.dimensionMapping + paramNames.keyPart + i + '-' + j] != undefined) {
                mapping = {
                    dimension: decodeURIComponent(parameters[paramNames.dimensionMapping + paramNames.keyPart + i + '-' + j]),
                    selectedChannel: decodeURIComponent(parameters[paramNames.dimensionMapping + paramNames.valuePart + i + '-' + j])
                };
                chartRow.dimensionMapping.push(mapping);
                j++;
            }
            j = 0;
            while (parameters[paramNames.measureMapping + paramNames.keyPart + i + '-' + j] != undefined) {
                mapping = {
                    dimension: decodeURIComponent(parameters[paramNames.measureMapping + paramNames.keyPart + i + '-' + j]),
                    selectedChannel: decodeURIComponent(parameters[paramNames.measureMapping + paramNames.valuePart + i + '-' + j])
                };
                chartRow.measureMapping.push(mapping);
                j++;
            }
            config.chartRows.push(chartRow);
            i++;
        }

        return config;
    },

    deserializeDatasets: function(parameters){
        var paramNames = Vis.navigation.paramNames, datasets = [], i = 0, dataset;
        while (parameters[paramNames.datasetsPrefix + i + paramNames.datasetsUri]) {
            dataset = new Vis.data.Dataset();
            dataset.uri = decodeURIComponent(parameters[paramNames.datasetsPrefix + i + paramNames.datasetsUri]);
            dataset.endpoint = decodeURIComponent(parameters[paramNames.datasetsPrefix + i + paramNames.datasetsEndpoint]);
            var j = 0;
            while (parameters[paramNames.datasetsPrefix + i + paramNames.datasetsDeletedMeasures + j]) {
                dataset.deletedMeasures.push(decodeURIComponent(parameters[paramNames.datasetsPrefix + i + paramNames.datasetsDeletedMeasures + j]));
                j++;
            }
            datasets.push(dataset);
            i++;
        }
        // for Backwards compatibility:
        if (datasets.length == 0 && parameters[paramNames.dataset]){
            dataset = new Vis.data.Dataset();
            dataset.uri = decodeURIComponent(parameters[paramNames.dataset]);
            if (parameters[paramNames.endpoint] == undefined || parameters[paramNames.endpoint] == "") {
                dataset.endpoint = "http://zaire.dimis.fim.uni-passau.de:8890/sparql";
            } else {
                dataset.endpoint = decodeURIComponent(parameters[paramNames.endpoint]);
            }
            datasets.push(dataset);
        }

        // Backward compatibility, but could be removed i guess (todo)...
        if (parameters[paramNames.deletedMeasures + 0] && datasets[0]){
            i = 0;
            datasets[0].deletedMeasures = [];
            while (parameters[paramNames.deletedMeasures + i] != undefined) {
                datasets[0].deletedMeasures.push(decodeURIComponent(parameters[paramNames.deletedMeasures + i]));
                i++;
            }
        }
        return datasets;
    },

    updateAddress: function () {
        if (Vis.view.isConfigurationChanging)
            return;
        // remove all parameters
        _.each($.address.parameterNames(), function(parameterName) {$.address.parameter(parameterName, '') });
        // set new parameters
        var parameters = [];
        _.each(Vis.navigation.serializeDatasets(), function(item){parameters.push(item)});
        _.each(Vis.navigation.serializeBaseToParameterArray(), function(item){parameters.push(item)});
        for (var i = 0; i < Vis.view.chartRows.length; i++) {
            _.each(Vis.navigation.serializeChartToParameterArray(i), function(item){parameters.push(item)});
        }
        _.each(Vis.navigation.serializePredicatesAndFilters(), function(item){parameters.push(item)});
        _.each(parameters, function(parameter){ $.address.parameter(parameter.name, parameter.value); });
        $.address.update();
    },

    serializeBaseToParameterArray: function(){
        var parameters = [];
        parameters.push({name: Vis.navigation.paramNames.showChartsOnly, value: Vis.view.showChartsOnly});
        if (Vis.view.zoom != 1)
            parameters.push({name: Vis.navigation.paramNames.zoom, value: Vis.view.zoom});
        return parameters;
    },

    serializeChartToParameterArray: function(chartRowIndex, targetIndex){
        var paramNames = Vis.navigation.paramNames;
        if (targetIndex == null ||targetIndex == undefined)
            targetIndex = chartRowIndex;
        var parameters = [];
        var chartRow = Vis.view.chartRows[chartRowIndex];
        var chartName = paramNames.emptyChartName;
        if (chartRow.selectedChart != null)
            chartName = chartRow.selectedChart.chartname;
        parameters.push({name: paramNames.selectedChart + targetIndex, value: chartName});
        parameters.push({name: paramNames.datasetIndex + targetIndex, value: chartRow.datasetIndex});
        parameters.push({name: paramNames.isConfigMenuOpen + targetIndex, value: chartRow.isConfigMenuOpen});
        if (chartRow.caption != null)
            parameters.push({name: paramNames.caption + targetIndex, value: encodeURIComponent(chartRow.caption)});
        for (var j = 0; j < chartRow.dimensionMapping.length; j++) {
            parameters.push({name: paramNames.dimensionMapping + paramNames.keyPart + targetIndex + '-' + j, value: encodeURIComponent(Vis.data.datasets[chartRow.datasetIndex].dimensions[j].label)});
            parameters.push({name: paramNames.dimensionMapping + paramNames.valuePart + targetIndex + '-' + j, value: encodeURIComponent(chartRow.dimensionMapping[j].selectedChannel)});
        }
        for (j = 0; j < chartRow.measureMapping.length; j++) {
            parameters.push({name: paramNames.measureMapping + paramNames.keyPart + targetIndex + '-' + j, value: encodeURIComponent(Vis.data.datasets[chartRow.datasetIndex].measures[j].label)});
            parameters.push({name: paramNames.measureMapping + paramNames.valuePart + targetIndex + '-' + j, value: encodeURIComponent(chartRow.measureMapping[j].selectedChannel)});
        }
        return parameters;
    },

    serializeDatasets: function(){
        var paramNames = Vis.navigation.paramNames;
        var parameters = [];
        for (var i = 0; i < Vis.data.datasets.length; i++) {
            _.each(Vis.navigation.serializeDataset(i, i), function(item){parameters.push(item)});
        }

        return parameters;
    },

    serializeDataset: function(datasetIndex, targetIndex){
        var paramNames = Vis.navigation.paramNames;
        var parameters = [];
        var dataset = Vis.data.datasets[datasetIndex];
        parameters.push({name: paramNames.datasetsPrefix + targetIndex + paramNames.datasetsUri, value: dataset.uri});
        parameters.push({name: paramNames.datasetsPrefix + targetIndex + paramNames.datasetsEndpoint, value: dataset.endpoint});
        for (var j = 0; j < dataset.deletedMeasures.length; j++) {
            parameters.push({name: paramNames.datasetsPrefix + targetIndex + paramNames.datasetsDeletedMeasures + j, value: dataset.deletedMeasures[j]});
        }
        return parameters;
    },

    serializePredicatesAndFilters: function () {
        var parameters = [];
        var paramNames = Vis.navigation.paramNames;
        var predicates = Vis.view.queryWizardPredicates;
        for (var i=0, max=predicates.length; i<max; i++){
            var filterPredicatePrefix = paramNames.predicate + i;
            parameters.push({name: filterPredicatePrefix, value: predicates[i]});
            for (var j = 0; j < Vis.view.datasetFilters.length; j++) {
                var filter = Vis.view.datasetFilters[j];
                if (filter.predicateUri == predicates[i]){
                    parameters.push({name: filterPredicatePrefix + paramNames.predicateFilterType, value: filter.type});
                    parameters.push({name: filterPredicatePrefix + paramNames.predicateFilterValue, value: encodeURIComponent(filter.value)});
                    parameters.push({name: filterPredicatePrefix + paramNames.predicateFilterLabel, value: encodeURIComponent(filter.valueLabel)});
                    break;
                }
            }
        }

        return parameters;
    }
};

Vis.urls = {
    getImageUrlFromUrl : function(chartUrl){
        return window.location.origin + "/phantom?url=" + encodeURIComponent(chartUrl + '&' + Vis.navigation.paramNames.showChartsOnly + "=true");
    },
    getUrlForSingleChart : function(chartRowIndex){
        var parameters = [];
        var chartUrl = window.location.origin + window.location.pathname+'#?';
        _.each(Vis.navigation.serializePredicatesAndFilters(), function(item){parameters.push(item)});
        _.each(Vis.navigation.serializeDataset(Vis.view.chartRows[chartRowIndex].datasetIndex, 0), function(item){parameters.push(item)});
        _.each(Vis.navigation.serializeChartToParameterArray(chartRowIndex, 0), function(item){parameters.push(item)});
        // change parameters:
        _.each(parameters, function(parameter){
            // Change DatasetId from Chart
            if (parameter.name == Vis.navigation.paramNames.datasetIndex + '0') { parameter.value = 0}
        });
        _.each(parameters, function(parameter){ chartUrl += parameter.name + '=' + parameter.value + '&'; });
        chartUrl = chartUrl.replace(/&$/,'');

        return chartUrl;
    },
    getDatasetUrl : function(datasetIndex){
        var parameters = [];
        var datasetUrl = window.location.origin + window.location.pathname+'#?';

        _.each(Vis.navigation.serializePredicatesAndFilters(), function(item){parameters.push(item)});
        _.each(Vis.navigation.serializeDataset(datasetIndex, 0), function(item){parameters.push(item)});
        _.each(parameters, function(parameter){ datasetUrl += parameter.name + '=' + parameter.value + '&'; });
        datasetUrl = datasetUrl.replace(/&$/,'');

        return datasetUrl;
    }
};

Vis.chartHelper = {
    indexOfChartNameInArray: function(chartname, array){
        for(var i=0; i<array.length; i++){
            if (array[i].chartname == chartname){
                return i;
            }
        }
        return -1;
    },
    cleanupChartServerData : function (dataReceived) {
        var charts = [];
        for(var i=0; i<dataReceived.length; i++){
            var chartIndex = Vis.chartHelper.indexOfChartNameInArray(dataReceived[i].chartname, charts);
            var chart = { possibleMappings: [] };
            if (chartIndex == -1){
                chart.chartname = dataReceived[i].chartname;
                charts.push(chart);
                chartIndex = charts.length-1;
            } else {
                chart = charts[chartIndex];
            }

            //chart.visualchannels = [];
            var mappingObjects = [];
            for (var j = 0; j < dataReceived[i].visualchannels.length; j++){
                var dimension = dataReceived[i].visualchannels[j].component.label;
                var channel = dataReceived[i].visualchannels[j].label;

                //chart.visualchannels.push({label: channel});
                mappingObjects.push({dimension: dimension, channel: channel});

            }
            chart.possibleMappings.push(mappingObjects);

            charts[chartIndex] = chart;
        }
        return charts;
    },
    getChartByName : function(datasetIndex, chartName){
        if (Vis.data.datasets.length == 0)
            return null;
        var charts = Vis.data.datasets[datasetIndex].charts;
        var chart = null;
        for (var i= 0, max = charts.length; i<max; i++){
            if (charts[i].chartname == chartName){
                chart = charts[i];
                break;
            }
        }
        return chart;
    }
};


Vis.configuration = {
    setChart: function(chartRowIndex, newChartName){
        if (Vis.view.chartRows[chartRowIndex].selectedChart != null && Vis.view.chartRows[chartRowIndex].selectedChart.chartname == newChartName)
            return;

        var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
        var $navigation = $getVisRow(chartRowIndex).find('nav.configuration'); //todo: dimensions & measures combined
        $navigation.find('button').removeClass('btn-success');
        Vis.view.chartRows[chartRowIndex].channelMappingChangedByHandStack = [];
        Vis.view.chartRows[chartRowIndex].selectedChart = Vis.chartHelper.getChartByName(datasetIndex, newChartName);
        if (Vis.view.chartRows[chartRowIndex].selectedChart == null){
            $navigation.find('.possibledimensions, .possiblevalues').hide();
            resetChartDimensions(chartRowIndex);
            resetChartMeasures(chartRowIndex);
            resetVis(chartRowIndex); // todo: bugfix: if no chart is selected, this reset does also reset the changed caption of the chart.
            return;
        }

        //if (Vis.view.chartRows[chartRowIndex].selectedChart.chartname == "columnchart")
        //    $navigation.find('.possiblecharts').find('button[data-chart=barchart]').addClass('btn-success');

        $navigation.find('button[data-chart=' + newChartName + ']').addClass('btn-success');
        resetAllDimensionChannels(chartRowIndex);
        resetAllMeasureChannels(chartRowIndex);
        resetChartOptions(chartRowIndex, newChartName);

        var mapping = Vis.view.chartRows[chartRowIndex].selectedChart.possibleMappings[0];
        for(var i=0; i<mapping.length; i++){
            var currentMappingPair = mapping[i];
            $navigation.find("li[data-dimension='" + currentMappingPair.dimension + "'] button .caption").html(currentMappingPair.channel); // finds dimensions and measures
            setChannelForDimensionOrMeasure(chartRowIndex, currentMappingPair.dimension, currentMappingPair.channel);
        }

        loadVisualization(chartRowIndex);
        showOrHideZoomButtonsForUnsupportedCharts(chartRowIndex);

        $navigation.find('.possibledimensions, .possiblevalues').show();
        Vis.navigation.updateAddress();
        console.log('selectedChart changed: ' + newChartName);
    },

    getEmptyChartRow : function(datasetIndex){
        datasetIndex = datasetIndex || 0;
        var chartRow = new Vis.view.ChartRow(datasetIndex);
        if (Vis.data.datasets.length == 0)
            return chartRow;
        for(var i = 0; i<Vis.data.datasets[datasetIndex].dimensions.length; i++){
            chartRow.dimensionMapping.push({selectedChannel : ""});
        }
        for(i = 0; i<Vis.data.datasets[datasetIndex].measures.length; i++){
            chartRow.measureMapping.push({selectedChannel : ""});
        }
        return chartRow;
    },

    setChartObjectCaption : function(chartRowIndex){
        var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
        var datasetName = 'Dataset ' + (datasetIndex + 1);
        if (Vis.data.datasets[datasetIndex] && Vis.data.datasets[datasetIndex].datasetName)
            datasetName = Vis.data.datasets[datasetIndex].datasetName;
        Vis.view.chartRows[chartRowIndex].caption = 'Chart ' + (chartRowIndex + 1) + ' - ' + datasetName;
    }
};

Vis.loading = {
    loadDatasetMetadata: function (datasetIndex, callback) {
        Vis.data.datasets[datasetIndex].dimensions = [];
        Vis.data.datasets[datasetIndex].measures = [];
        if (Vis.data.datasets[datasetIndex].uri == "" || Vis.data.datasets[datasetIndex].endpoint == "") {
            if (callback != undefined)
                callback(false, datasetIndex);
            return;
        }
        Vis.view.loadingStarted();
        console.log('loading DatasetMetadata...');

        var cmd = "getPreviewAuto";
        $.post("/viz", { cmd: cmd, chart: '', dataset: Vis.data.datasets[datasetIndex].uri, dimension: '', endpoint: Vis.data.datasets[datasetIndex].endpoint, deletedmeasures: JSON.stringify(Vis.data.datasets[datasetIndex].deletedMeasures), datasetFilters: JSON.stringify(Vis.view.datasetFilters), chartrowindex: ""},
            function (dataReceived) {
                //console.log(dataReceived);
                if (dataReceived.error != null) {
                    alert(dataReceived.error); // Please do NOT add $('#loadingindicator').hide(); here. This is the job of "Vis.view.loadingFinished()" - and if there is a bug, tell GT
                    Vis.view.loadingFinished();
                    if (callback != undefined)
                        callback(false, datasetIndex);
                    return;
                }
                loadDatasetLabel(datasetIndex);
                console.log('getPreviewAuto finished...');
                Vis.data.datasets[datasetIndex].charts = Vis.chartHelper.cleanupChartServerData(dataReceived);
                $.post("/viz", { cmd: "getDimension", dataset: Vis.data.datasets[datasetIndex].uri, endpoint: Vis.data.datasets[datasetIndex].endpoint},
                    function (dataReceived) {
                        console.log('getDimension finished...');
                        Vis.data.datasets[datasetIndex].dimensions = dataReceived;
                        $.post("/viz", { cmd: "getMeasure", dataset: Vis.data.datasets[datasetIndex].uri, endpoint: Vis.data.datasets[datasetIndex].endpoint, deletedmeasures: JSON.stringify(Vis.data.datasets[datasetIndex].deletedMeasures)},
                            function (dataReceived) {
                                console.log('getMeasure finished.');
                                Vis.data.datasets[datasetIndex].measures = dataReceived;
                                Vis.loading.loadDatasetMetadataFinished(datasetIndex);
                                Vis.view.loadingFinished();
                                if (Vis.config.debug) $('button[data-chart=bubblechart]').click();
                                if (callback != undefined)
                                    callback(true, datasetIndex);
                            }, "json")
                            .error(function () {
                                alert("Error while loading measures.");
                                if (callback != undefined)
                                    callback(false, datasetIndex);
                            });
                    }, "json")
                    .error(function () {
                        alert("Error while loading dimensions.");
                        if (callback != undefined)
                            callback(false, datasetIndex);
                    });
            }, "json")
            .error(function (jqXHR, textStatus, errorThrown) {
                if (jqXHR.readyState != 0) { // workaround for problem when navigating while request is in progress...
                    alert("Error while showing supported charts.");
                } else {
                    console.log("Error while showing supported charts.");
                }
                if (callback != undefined)
                    callback(false, datasetIndex);
            });
    },

    // Vis.loading
    loadDatasetMetadataFinished: function (datasetIndex) {
        Vis.view.resetMultipleCharts(datasetIndex);
        for (var i = 0, max = Vis.view.chartRows.length; i < max; i++) {
            if (Vis.view.chartRows[i].datasetIndex == datasetIndex) {
                resetChartTypes(i);
                resetChartDimensions(i);
                resetChartMeasures(i);
                resetVis(i);
            }
        }
        Vis.data.datasets[datasetIndex].receivedDataRows = null;
    }
};


Vis.ui = {
    bookmark: function(chartRowIndex){
        $.ajax({
            url:"/query/save_visualization",
            type:"POST",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify({ label: Vis.view.chartRows[chartRowIndex].caption, description:"", url:Vis.urls.getUrlForSingleChart(chartRowIndex) })
        })
            .success(function(e){
                Vis.ui.alert('Your Chart was successfully saved. Do you want to switch to <a href="' + e.redirect_url + '">42data</a>?', 'Successfully saved', function(){
                    window.location.href = e.redirect_url;
                });
            })
            .error(function(e){
                Vis.ui.alert('Error occured...', 'Error');
            });
    },

    alert: function(body, title, okayCallback, cancelCallback){
        title = title || 'Meldung';
        var $modal = $('#modal-message');
        $modal.find('.modal-title').html(title);
        $modal.find('.modal-body').html(body);
        if (okayCallback){
            $modal.find('.modal-footer button.modal-ok').on('click', okayCallback);
        } else {
            $modal.find('.modal-footer button.modal-ok').hide();
        }
        if (cancelCallback){
            $modal.find('.modal-footer button.modal-close').on('click', cancelCallback);
        }
        return $modal.modal();
    }
};


Vis.chart = {
    addNewDatasetAndChart: function(endpoint, dataset){
        Vis.view.loadingStarted();
        var newDataset = new Vis.data.Dataset();
        newDataset.uri = dataset;
        newDataset.endpoint = endpoint;
        newDataset.deletedMeasures = [];
        newDataset.isDirty = true;
        Vis.data.datasets.push(newDataset);
        var datasetIndex = Vis.data.datasets.length - 1;
        addNewVisualisation(datasetIndex);
        Vis.view.loadingFinished();
    }
};

// Vis.chart
function resetChartTypes(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var $visRow = $getVisRow(chartRowIndex);
    $visRow.find(".possiblecharts button").addClass('disabled');
    for (var i=0; i<Vis.data.datasets[datasetIndex].charts.length; i++){
        if (Vis.data.datasets[datasetIndex].charts[i].chartname == "scatterplot"){ // workaround for "scatterplot == bubblechart" behaviour
            Vis.data.datasets[datasetIndex].charts[i].chartname = "bubblechart";
        }
        var chart = Vis.data.datasets[datasetIndex].charts[i].chartname;
        $visRow.find('.possiblecharts button[data-chart=' + chart + ']').removeClass('disabled');
    }
    bindChartButtons(chartRowIndex);
}

// Vis.chart
function resetVis(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var $visRow = $getVisRow(chartRowIndex);
    $visRow.find('.vis-container .vis').empty();
    $visRow.find('.vis-container .zoomIn, .vis-container .zoomOut').show();
    Vis.view.chartRows[chartRowIndex] = Vis.configuration.getEmptyChartRow(datasetIndex);
    Vis.view.setChartRowCaption(chartRowIndex, $visRow);
    showChartConfiguration(chartRowIndex);
}

// Vis.loading
function getDataTypeFromUrl(dataTypeUrl){
    return dataTypeUrl.substr(dataTypeUrl.lastIndexOf('#')+1);
}

// Vis.chart
function resetChartDimensions(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var $visRow = $getVisRow(chartRowIndex);
    var $possibleDimensionsUl = $visRow.find('.possibledimensions > ul').first();
    $possibleDimensionsUl.empty();
    var $dimensionTemplate = $('#dimensiontemplate');
    if (Vis.data.datasets.length == 0)
        return;
    for(var i = 0; i < Vis.data.datasets[datasetIndex].dimensions.length; i++){
        Vis.view.chartRows[chartRowIndex].dimensionMapping[i].selectedChannel = "";
        var dimension = Vis.data.datasets[datasetIndex].dimensions[i].label;
        if(dimension == null){
            alert('Dimension can not be shown');
            continue;
        }
        var $newRow = $dimensionTemplate.clone().removeAttr('id').attr('data-dimension', dimension);
        $newRow.find('label').html(dimension).attr('title', dimension);/*.click(function(){
            var $currentItem = $(this);
            Vis.view.getNewAxisLabel($currentItem.html(), function(newLabel){ $currentItem.html(newLabel).attr('title', newLabel); });
        });*/
        $newRow.find('.button-remove').remove();
        $possibleDimensionsUl.append($newRow);
    }
}

// Vis.chart
// todo: dimension & measure mixed
function resetChartMeasures(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var $visRow = $getVisRow(chartRowIndex);
    var $possibleMeasuresUl = $visRow.find('.possiblevalues > ul').first();
    $possibleMeasuresUl.empty();
    var $dimensionTemplate = $('#dimensiontemplate');
    if (Vis.data.datasets.length == 0)
        return;
    for(var i = 0; i < Vis.data.datasets[datasetIndex].measures.length; i++){
        Vis.view.chartRows[chartRowIndex].measureMapping[i].selectedChannel = "";
        var measure = Vis.data.datasets[datasetIndex].measures[i].label;
        if(measure == null){
            alert('Dimension can not be shown');
            continue;
        }
        var $newRow = $dimensionTemplate.clone().removeAttr('id').attr('data-dimension', measure);
        $newRow.find('label').html(measure).attr('title', measure);
        $newRow.find('.button-remove').click(removeMeasureClicked);
        if (Vis.data.datasets[datasetIndex].measures.length == 1){
            $newRow.find('.button-remove').remove();
        }
        $possibleMeasuresUl.append($newRow);
    }
}

// Vis.configuration
function removeMeasureClicked(){
    var chartRowIndex = getChartRowIndex($(this));
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var measure = $(this).parent('li').hide('slow').data('dimension');
    console.log('delete measure ' + measure);
    for (var i=0; i<Vis.data.datasets[datasetIndex].measures.length; i++){
        if (Vis.data.datasets[datasetIndex].measures[i].label == measure){
			// remove every URL parameter; leave only: dataset, endpoint & deletedMeasures
            var allParameters = $.address.parameterNames();
            var prefixDataset = Vis.navigation.paramNames.datasetsPrefix + datasetIndex;
            var prefixDatasetDeletedMeasure = Vis.navigation.paramNames.datasetsPrefix + datasetIndex + Vis.navigation.paramNames.datasetsDeletedMeasures;
            for (var j=0; j<allParameters.length; j++){
                if (allParameters[j].substring(0, prefixDataset.length) == prefixDataset
                    && allParameters[j] != prefixDataset + Vis.navigation.paramNames.datasetsUri
                    && allParameters[j] != prefixDataset + Vis.navigation.paramNames.datasetsEndpoint
                    && allParameters[j].substring(0, prefixDatasetDeletedMeasure.length) != prefixDatasetDeletedMeasure){
                    $.address.parameter(allParameters[j], '');
                }
            }
            $.address.parameter(prefixDatasetDeletedMeasure + Vis.data.datasets[datasetIndex].deletedMeasures.length, Vis.data.datasets[datasetIndex].measures[i].measureuri);
            $.address.update();
            break;
        }
    }
}

// Vis.configuration
function channelConfigChanged(e){
    e.preventDefault();
    var dimension = $(this).closest('li').parent().closest('li').data('dimension');
    var channel = $(this).data('channel');
    var chartRowIndex = getChartRowIndex($(this));
    console.log('click: row ' + chartRowIndex + ': ' + dimension+': '+channel);
    if (!hasChannelChangedForDimension(chartRowIndex, dimension, channel)){
        console.log('Channel did not change, so do nothing...');
        return;
    }
    //$(this).closest('.btn-group').find('.caption').html(channel);
    Vis.view.chartRows[chartRowIndex].channelMappingChangedByHandStack.push({dimension: dimension, channel: channel});
    setChannelForDimensionOrMeasure(chartRowIndex, dimension, channel);
    setChannelsForOtherDimensionsOrMeasuresAutomatically(chartRowIndex, dimension, channel);
    loadVisualization(chartRowIndex);
    Vis.navigation.updateAddress();
}

// Vis.chartHelper
function getChartRowIndex($elementWithinRow){
    return $elementWithinRow.parents('.vis-row').data('vis-row-index');
}

// Vis.chart
function hasChannelChangedForDimension(chartRowIndex, dimension, channel){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex, i;
    for (i=0; i<Vis.data.datasets[datasetIndex].dimensions.length; i++){
        if (Vis.data.datasets[datasetIndex].dimensions[i].label == dimension){
            //return globals.dimensions[i].selectedChannel != channel;
            return Vis.view.chartRows[chartRowIndex].dimensionMapping[i].selectedChannel != channel;
        }
    }
    for (i=0; i<Vis.data.datasets[datasetIndex].measures.length; i++){
        if (Vis.data.datasets[datasetIndex].measures[i].label == dimension){
            //return globals.measures[i].selectedChannel != channel;
            return Vis.view.chartRows[chartRowIndex].measureMapping[i].selectedChannel != channel;
        }
    }
    return false;
}

// Vis.chart
function setChannelForDimensionOrMeasure(chartRowIndex, dimension, channel){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    for (var i=0; i<Vis.data.datasets[datasetIndex].dimensions.length; i++){
        if (Vis.data.datasets[datasetIndex].dimensions[i].label == dimension){
            //globals.dimensions[i].selectedChannel = channel;
            if (Vis.view.chartRows[chartRowIndex].dimensionMapping[i].selectedChannel == channel)
                return false;
            Vis.view.chartRows[chartRowIndex].dimensionMapping[i].selectedChannel = channel;
            $getVisRow(chartRowIndex).find('nav.configuration').find("li[data-dimension='" + dimension + "'] button .caption").html(channel);
            return true;
        }
    }
    for (i=0; i<Vis.data.datasets[datasetIndex].measures.length; i++){
        if (Vis.data.datasets[datasetIndex].measures[i].label == dimension){
            //globals.measures[i].selectedChannel = channel;
            if (Vis.view.chartRows[chartRowIndex].measureMapping[i].selectedChannel == channel)
                return false;
            Vis.view.chartRows[chartRowIndex].measureMapping[i].selectedChannel = channel;
            $getVisRow(chartRowIndex).find('nav.configuration').find("li[data-dimension='" + dimension + "'] button .caption").html(channel);
            return true;
        }
    }
    return false;
}

// Vis.configuration
function setChannelsForOtherDimensionsOrMeasuresAutomatically(chartRowIndex, dimensionChanged, channelSelected){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex, i, k;
    var mostAccurateMapping = getMostAccurateMapping(chartRowIndex, dimensionChanged, channelSelected);
    for (i=0; i<Vis.data.datasets[datasetIndex].dimensions.length; i++){
        if (Vis.data.datasets[datasetIndex].dimensions[i].label != dimensionChanged){
            for (k=0; k<mostAccurateMapping.length; k++){
                if (mostAccurateMapping[k].dimension == Vis.data.datasets[datasetIndex].dimensions[i].label){
                    setChannelForDimensionOrMeasure(chartRowIndex, Vis.data.datasets[datasetIndex].dimensions[i].label, mostAccurateMapping[k].channel);
                    break;
                }
            }
        }
    }
    for (i=0; i<Vis.data.datasets[datasetIndex].measures.length; i++){
        if (Vis.data.datasets[datasetIndex].measures[i].label != dimensionChanged){
            for (k=0; k<mostAccurateMapping.length; k++){
                if (mostAccurateMapping[k].dimension == Vis.data.datasets[datasetIndex].measures[i].label){
                    setChannelForDimensionOrMeasure(chartRowIndex, Vis.data.datasets[datasetIndex].measures[i].label, mostAccurateMapping[k].channel);
                    break;
                }
            }
        }
    }
}

// Vis.chart
function getMostAccurateMapping(chartRowIndex, dimensionChanged, channelSelected){
    var availableMappings = filterAvailableMappings(dimensionChanged, channelSelected, Vis.view.chartRows[chartRowIndex].selectedChart.possibleMappings);
    for (var i=Vis.view.chartRows[chartRowIndex].channelMappingChangedByHandStack.length-1; i>=0; i--){
        if (Vis.view.chartRows[chartRowIndex].channelMappingChangedByHandStack[i].dimension == dimensionChanged){
            continue;
        }
        if (availableMappings.length > 1){
            var availableMappingsNew = filterAvailableMappings(Vis.view.chartRows[chartRowIndex].channelMappingChangedByHandStack[i].dimension, Vis.view.chartRows[chartRowIndex].channelMappingChangedByHandStack[i].channel, availableMappings);
            if (availableMappingsNew.length == 0){
                break;
            }
            availableMappings = availableMappingsNew;
        }
    }
    if (availableMappings.length>0){
        return availableMappings[0];
    }
    console.log('No Suggestion found... ');
    return null;
}

// Vis.configuration
function filterAvailableMappings(filterDimension, filterChannel, availableMappings){
    var filteredMappings = [];
    for (var i=0; i<availableMappings.length; i++){
        var mapping = availableMappings[i];
        for (var j=0; j<mapping.length; j++){
            if (mapping[j].dimension == filterDimension && mapping[j].channel == filterChannel){
                filteredMappings.push(mapping);
                break;
            }
        }
    }
    return filteredMappings;
}

// Vis.chart
function getPossibleChannelsForDimension(chartRowIndex, dimension){
    var possibleChannels = [];
    for(var j=0; j<Vis.view.chartRows[chartRowIndex].selectedChart.possibleMappings.length; j++){
        for(var k=0; k<Vis.view.chartRows[chartRowIndex].selectedChart.possibleMappings[j].length; k++){
            if (Vis.view.chartRows[chartRowIndex].selectedChart.possibleMappings[j][k].dimension == dimension){
                if ($.inArray(Vis.view.chartRows[chartRowIndex].selectedChart.possibleMappings[j][k].channel, possibleChannels) == -1){
                    possibleChannels.push(Vis.view.chartRows[chartRowIndex].selectedChart.possibleMappings[j][k].channel);
                    
                }
            }
        }
    }
    return possibleChannels;
}

// Vis.chart
function resetAllDimensionChannels(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var $navigation = $getVisRow(chartRowIndex).find('nav.configuration');
    for(var i=0; i<Vis.data.datasets[datasetIndex].dimensions.length; i++){
        var possibleChannels = getPossibleChannelsForDimension(chartRowIndex, Vis.data.datasets[datasetIndex].dimensions[i].label);
        var $dimensionRow = $navigation.find("li[data-dimension='" + Vis.data.datasets[datasetIndex].dimensions[i].label + "']");
        showOrHideChannelConfig($dimensionRow, possibleChannels);
    }
}

// Vis.chart
function resetAllMeasureChannels(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var $navigation = $getVisRow(chartRowIndex).find('nav.configuration');
    for(var i=0; i<Vis.data.datasets[datasetIndex].measures.length; i++){
        var possibleChannels = getPossibleChannelsForDimension(chartRowIndex, Vis.data.datasets[datasetIndex].measures[i].label);
        var $measureRow = $navigation.find("li[data-dimension='" + Vis.data.datasets[datasetIndex].measures[i].label + "']");
        showOrHideChannelConfig($measureRow, possibleChannels);
    }
}

// Vis.configuration
function showOrHideChannelConfig($configRow, possibleChannels){
    if (possibleChannels.length == 1){
        $configRow.find(".btn-group").hide();
        $configRow.find(".captionSingle").html(possibleChannels[0]).show();
    } else {
        $configRow.find(".btn-group").show();
        $configRow.find(".captionSingle").hide();
        var $configRowMenu = $configRow.find(".dropdown-menu");
        $configRowMenu.empty();
        for(var j=0; j<possibleChannels.length; j++){
            var $newValue = $('<li><a data-channel="' + possibleChannels[j] + '">' + possibleChannels[j] + '</a></li>');
            $newValue.find('a').on('click', channelConfigChanged);
            $configRowMenu.append($newValue);
        }
    }
}

// Vis.chart
function showOrHideZoomButtonsForUnsupportedCharts(chartRowIndex){
    var chartName = Vis.view.chartRows[chartRowIndex].selectedChart.chartname;
    var $visRow = $getVisRow(chartRowIndex);
    if (chartName == 'parallelcoordinates' || chartName == 'table'){
        $visRow.find('.zoomIn, .zoomOut').hide();
    } else {
        $visRow.find('.zoomIn, .zoomOut').show();
    }
}

// Vis.chart
function loadVisualization(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    //if (Vis.view.receivedDataRows == null){
    if (Vis.data.datasets[datasetIndex].receivedDataRows == null){
        loadVisualizationFromServer(chartRowIndex);
        return;
    }

    var chartName = Vis.view.chartRows[chartRowIndex].selectedChart.chartname;
    if (chartName != 'bubblechart' && chartName != 'linechart' && chartName != 'barchart'){
        return loadVisualizationFromServer(chartRowIndex);
    }
    var channelMappingsForViz = getChannelMappingForViz(chartRowIndex);
    $getVisRow(chartRowIndex).find(".vis").empty();
    chartFactory_callVisualise(chartName, Vis.data.datasets[datasetIndex].receivedDataRows, channelMappingsForViz, '#vis-row' + chartRowIndex + ' .vis', chartRowIndex); //, returnedData.legendDictionary
}

// Vis.chart
function loadVisualizationFromServer(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    Vis.view.loadingStarted();
    var chartRowConfig = Vis.view.chartRows[chartRowIndex];
    var chartName = chartRowConfig.selectedChart.chartname;
    var dimensionMappings = getDimensionMappingForServer(chartRowIndex);

    $.post("/viz", { cmd: "getVisualization", chart: chartName, dataset: Vis.data.datasets[datasetIndex].uri, dimension:JSON.stringify(dimensionMappings), endpoint:Vis.data.datasets[datasetIndex].endpoint, deletedmeasures: JSON.stringify(Vis.data.datasets[datasetIndex].deletedMeasures), datasetFilters: JSON.stringify(Vis.view.datasetFilters), chartrowindex: chartRowIndex}, function(returnedData) {
            $getVisRow(chartRowIndex).find(".vis").empty();
            if (returnedData.start == ""){
                var channelMappingsForViz = getChannelMappingForViz(chartRowIndex);
                if (chartName == 'bubblechart' || chartName == 'linechart' || chartName == 'barchart')
                    Vis.data.datasets[datasetIndex].receivedDataRows = returnedData.rows;
                chartFactory_callVisualise(chartName, returnedData.rows, channelMappingsForViz, '#vis-row' + chartRowIndex + ' .vis', chartRowIndex, returnedData.legendDictionary);
            } else {
                visualizeWithEval(chartRowIndex, returnedData);
            }
            Vis.view.loadingFinished();
        }, "json")
        .error(function() {alert("Error while preparing preview."); });
}

// Vis.chart
function getDimensionMappingForServer(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var dimensionMappings = [];
    for(var i=0; i<Vis.data.datasets[datasetIndex].dimensions.length; i++){
        var dimension = Vis.data.datasets[datasetIndex].dimensions[i];
        var dimensionSelectedChannel = Vis.view.chartRows[chartRowIndex].dimensionMapping[i].selectedChannel;
        dimensionMappings.push({'label':dimension.label, 'dimensionuri':dimension.dimensionuri, 'cubecomponent':dimensionSelectedChannel, 'index': i}); // ** Belgin: Dieser Vermerk ist wichtig für Testzwecke
    }
    //console.log(dimensionMappings);
    return dimensionMappings;
}

// Vis.chart
function getChannelMappingForViz(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var channelMappingsForViz = [];
    for(var i=0; i<Vis.data.datasets[datasetIndex].dimensions.length; i++){
        var dimension = Vis.data.datasets[datasetIndex].dimensions[i];
        var dimensionSelectedChannel = Vis.view.chartRows[chartRowIndex].dimensionMapping[i].selectedChannel;
        channelMappingsForViz.push({label:dimension.label, channel:dimensionSelectedChannel, datatype: getDataTypeFromUrl(dimension.datatype), uri:dimension.dimensionuri, type:'dimension'});
    }
    for(i=0; i<Vis.data.datasets[datasetIndex].measures.length; i++){
        var measure = Vis.data.datasets[datasetIndex].measures[i];
        var measureSelectedChannel = Vis.view.chartRows[chartRowIndex].measureMapping[i].selectedChannel;
        channelMappingsForViz.push({label:measure.label, channel:measureSelectedChannel, datatype: getDataTypeFromUrl(measure.datatype), uri:measure.measureuri, type:'measure'});
    }
    return channelMappingsForViz;
}

// Vis.chart
function resetChartOptions(chartRowIndex, chartname){
    $getVisRow(chartRowIndex).find('.possibleoptions').hide();
    //if (chartname == 'barchart'){
    //    $('.possibleoptions').show();
    //}
}

// Vis.chart
function visualizeWithEval(chartRowIndex, dt){
    $getVisRow(chartRowIndex).find(".vis").html('<div id="vis-inner' + chartRowIndex + '" class="vis-inner"></div>');
    var start = dt.start;
    if(start == null){
        alert("Chart  could not be generated");
        return;
    }
    var channelMappings = channelMappingsForViz = getChannelMappingForViz(chartRowIndex)
    var config = {location:"vis-inner"+chartRowIndex, height:"600", width:"700"};
    //console.log(start);
    eval(start);
    brushingObserver.initializeSelfUpdate(chartRowIndex);
}

// Vis.chart
function addNewVisualisation(datasetIndex){
    datasetIndex = datasetIndex || 0;
    var $visRows = $('.vis-row');
    var chartRowIndex = $visRows.length;
    var $newVisRow = $('.vis-row.template').clone().removeClass('template').attr('id', 'vis-row' + chartRowIndex).data('chartRowIndex', chartRowIndex).data('datasetIndex', datasetIndex);
    $newVisRow.find('.vis').empty();
    Vis.view.chartRows.push(Vis.configuration.getEmptyChartRow(datasetIndex));
    Vis.configuration.setChartObjectCaption(Vis.view.chartRows.length-1);
    $visRows.last().after($newVisRow);
    bindChartButtons(chartRowIndex);
    initializeVisRow(chartRowIndex);
    Vis.configuration.setChart(chartRowIndex, '');
    Vis.view.setChartRowCaption(chartRowIndex, $newVisRow);
    $(window).scrollTop($newVisRow.position().top);
    Vis.navigation.updateAddress();
}

// Vis.chart
function removeChartRow(chartRowIndex) {
    brushingObserver.unregister(chartRowIndex);
    var $visRowToDelete = $getVisRow(chartRowIndex);
    $visRowToDelete.remove();
    Vis.view.chartRows.splice(chartRowIndex, 1);
    Vis.view.updateChartRowData();
    Vis.navigation.updateAddress();
    //brushingObserver.unregister(chartRowIndex);
    //var $visRowToHide = $getVisRow(chartRowIndex);
    //$visRowToHide.empty();
    //Vis.view.chartRows[chartRowIndex].isHidden = true;
    //Vis.navigation.updateAddress();
}

// Vis.chart.
function isChartConfigurationVisible(chartRowIndex){
    var $visRow = $getVisRow(chartRowIndex);
    return $visRow.find('.configuration').css('display') != 'none';
}

// Vis.chart
function hideAllChartConfigurationBut(chartRowIndexConfiguring){
    $('.configuration:visible').each(function(){
        var currentChartRowIndex = getChartRowIndex($(this));
        if (currentChartRowIndex != chartRowIndexConfiguring){
            hideChartConfiguration(currentChartRowIndex);
        }
    });
    showChartConfiguration(chartRowIndexConfiguring);
}

// Vis.chart.
function hideChartConfiguration(chartRowIndexConfiguring){
    var $visRow = $getVisRow(chartRowIndexConfiguring);
    if ($visRow.find('.configuration').css('display') == 'none')
        return false;
    $visRow.find('.configuration').hide(Vis.config.hideShowConfigSpeed, function(){
        $visRow.find('button.close-config-vis, button.add-vis, button.add-vis-aggregate, button.bookmark').hide();
        $visRow.find('button.config-vis').show();
    });
    $visRow.find('.vis-container').animate({'margin-left': 45}, Vis.config.hideShowConfigSpeed);
    $visRow.find('.config-vis-buttons').animate({'margin-left': 0}, Vis.config.hideShowConfigSpeed);
    Vis.view.chartRows[chartRowIndexConfiguring].isConfigMenuOpen = false;
    return true;
}

// Vis.chart.
function showChartConfiguration(chartRowIndexConfiguring){
    var $visRow = $getVisRow(chartRowIndexConfiguring);
    if ($visRow.find('.configuration').css('display') != 'none')
        return false;
    $visRow.find('button.config-vis').hide();
    $visRow.find('button.close-config-vis, button.add-vis, button.add-vis-aggregate, button.bookmark').show();
    $visRow.find('.configuration').show(Vis.config.hideShowConfigSpeed);
    $visRow.find('.config-vis-buttons').animate({'margin-left': 300}, Vis.config.hideShowConfigSpeed);
    $visRow.find('.vis-container').animate({'margin-left': 350}, Vis.config.hideShowConfigSpeed);
    Vis.view.chartRows[chartRowIndexConfiguring].isConfigMenuOpen = true;
    return true;
}

// Vis.chart.
function $getVisRow(chartRowIndex){
    return $('#vis-row' + chartRowIndex);
}

// Vis.chart
function initializeVisRow(chartRowIndex){
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var $visRow = $getVisRow(chartRowIndex);
    $visRow
        .data('vis-row-index', chartRowIndex)
        .find('.possibleoptions button').on('click', function(){
            var chartRowIndex = getChartRowIndex($(this));
            Vis.configuration.setChart(chartRowIndex, $(this).data('chart'));
        });
    $visRow.find('.zoomIn').on('click', zoomIn);
    $visRow.find('.zoomOut').on('click', zoomOut);
    if (chartRowIndex != 0){
        $visRow.find('.remove-vis').show().on('click', function(e){
            var chartRowIndex = getChartRowIndex($(this));
            e.preventDefault();
            if (isChartConfigurationVisible(chartRowIndex))
                showChartConfiguration(chartRowIndex-1);
            removeChartRow(chartRowIndex);
        });
    }
    $visRow.find('.add-vis').off('click').on('click', function(){addNewVisualisation(datasetIndex)});
    $visRow.find('.add-vis-aggregate').off('click').on('click', function(){showAggregateModal(datasetIndex)});
    $visRow.find('.bookmark').off('click').on('click', function(){Vis.ui.bookmark(datasetIndex)});
    if (!Vis.config.isLoggedIntoFortytwo)
        $visRow.find('.bookmark').remove();
    $visRow.find('h1').off('click').on('click', function(){Vis.view.showChartCaptionModal(getChartRowIndex($(this)))});
    bindEditConfigButton(chartRowIndex);
    hideAllChartConfigurationBut(chartRowIndex);
    resetChartTypes(chartRowIndex);
}

// Vis.chart
function bindChartButtons(chartRowIndex){
    $getVisRow(chartRowIndex).find('.possiblecharts').find('button:not(.disabled)').off('click').on('click',function(){
        var chartRowIndexClicked = getChartRowIndex($(this));
        Vis.configuration.setChart(chartRowIndexClicked, $(this).data('chart'));
    });
}

// Vis.chart
function bindEditConfigButton(chartRowIndex){
    var $visRow = $getVisRow(chartRowIndex);
    $visRow.find('button.config-vis').on('click', function(){
        var chartRowIndex = getChartRowIndex($(this));
        hideAllChartConfigurationBut(chartRowIndex);
        Vis.navigation.updateAddress();
    });
    $visRow.find('button.close-config-vis').on('click', function(){
        var chartRowIndex = getChartRowIndex($(this));
        hideChartConfiguration(chartRowIndex);
        Vis.navigation.updateAddress();
    });
}

// Vis.configuration
function zoomIn(){
    var $vis = $(this).parents('.vis-container').find('.vis');
    var height = $vis.height();
    var width = $vis.width();
    $vis.height(height*1.1);
    $vis.width(width*1.1);
}

// Vis.configuration
function zoomOut(){
    var $vis = $(this).parents('.vis-container').find('.vis');
    var height = $vis.height();
    var width = $vis.width();
    $vis.height(height*0.9);
    $vis.width(width*0.9);
}

// Vis.loading
function loadRandomChart(chartRowIndex) {
    chartRowIndex =  chartRowIndex || 0;
    var datasetIndex = Vis.view.chartRows[chartRowIndex].datasetIndex;
    var historyStateBefore = $.address.history();
    $.address.history(false);
    var randomIndex = randomFromInterval(0, Vis.data.datasets[datasetIndex].charts.length - 1);
    Vis.view.isConfigurationChanging = true;
    Vis.configuration.setChart(0, Vis.data.datasets[datasetIndex].charts[randomIndex].chartname);
    Vis.view.isConfigurationChanging = false;
    Vis.navigation.updateAddress();
    $.address.history(historyStateBefore);
    /*
    DataTypeRecognition:
        - Date
        - Currency
        - Percentage
    Better suggestion algorithm:
    ?1: is there a date-related dimension
        - go through all dimensions
          - get distinct values
            - are all values 4 letters long (and not less) --> probably a year --> ansteigend? reihenfolge gleicher abstand (2009, 2010)? im zeitbereich 1800-2020? dann definitiv ein jahr
            - is the fromat like XX.XX.XXXX (or XX/XX/XX or XXXX-XX-XX or ...) with only numbers--> probably a date
            - are the values like "Monday, Thuseday, ..." or "January, April, ..." -->

    Data Range: what is the data range? can we suggest
    * */
}

// Vis.helper
function randomFromInterval(from, to) {
    return Math.floor(Math.random() * (to - from + 1) + from);
}

// Vis.configuration
function isMappingValid(possibleMappings, mapping){
    for (var j=0; j<possibleMappings.length; j++){
        var currentPossibleMapping = possibleMappings[j];
        var found=true;
        //console.log('currentPossibleMapping: ');
        for(var k=0; k<currentPossibleMapping.length; k++){
            var selectedChannel = "";
            //console.log('   ' + currentPossibleMapping[k].dimension + ': ' + currentPossibleMapping[k].channel);
            for(var l=0; l<mapping.length; l++){
                if (currentPossibleMapping[k].dimension == mapping[l].dimension){
                    selectedChannel = mapping[l].selectedChannel;
                    break;
                }
            }
            if (currentPossibleMapping[k].channel != selectedChannel){
                found=false;
            }
        }
        if (found)
            return true;
    }
    return false;
}


Vis.mindmeister = {

    getChartNode : function(chartRowIndex){
        var chartUrl = Vis.urls.getUrlForSingleChart(chartRowIndex);
        var mindMapChild = {
            title: $getVisRow(chartRowIndex).find('h1').html(),
            link: chartUrl,
            image: { url: Vis.urls.getImageUrlFromUrl(chartUrl)}
            //image: { url: 'http://code.know-center.tugraz.at/phantom?url=http%3A%2F%2Fcode.know-center.tugraz.at%2Fvis%23%3Fds0u%3Dhttp%3A%2F%2Fogd.ifs.tuwien.ac.at%2Fvienna%2Fb02-austrianprovinces-vie-dc%26ds0e%3Dvienna-lod%26%26chart0%3Dtable%26chartDsIn0%3D0%26confOp0%3Dfalse%26dimKey0-0%3DrefSex%26dimVal0-0%3Dcolumn%26dimKey0-1%3DrefDate%26dimVal0-1%3Dcolumn%26dimKey0-2%3DrefState%26dimVal0-2%3Dcolumn%26dimKey0-3%3DrefDistrict%26dimVal0-3%3Dcolumn%26msKey0-0%3DPop_total%26msVal0-0%3Dcolumn%26msKey0-1%3DBorn_state%26msVal0-1%3Dcolumn%26chart1%3Dempty%26chartDsIn1%3D0%26confOp1%3Dtrue%26dimKey1-0%3DrefSex%26dimKey1-1%3DrefDate%26dimKey1-2%3DrefState%26dimKey1-3%3DrefDistrict%26msKey1-0%3DPop_total%26msKey1-1%3DBorn_state%26chartsonly%3Dtrue'}
        };
        return mindMapChild;
    },

    getDatasetNode : function(datasetIndex){
        var datasetUrl = Vis.urls.getDatasetUrl(datasetIndex);
        var datasetName = Vis.data.datasets[datasetIndex].datasetName || 'Dataset ' + (datasetIndex + 1);
        var mindMapChild = {
            title: datasetName,
            link: datasetUrl,
            children: []
        };
        return mindMapChild;
    }
};

// Vis.ui
function showVisualisationsOnMindMap() {
    var mindMap = {
        map_version: '2.2',
        keep_aligned: true,
        root: {
            link: location.href,
            title: 'CODE Data Cube',
            children: []
        }
    };

    if (Vis.data.datasets.length > 1){
        // multiple Datasets
        _.each(Vis.data.datasets, function(dataset, datasetIndex){
            mindMap.root.children.push(Vis.mindmeister.getDatasetNode(datasetIndex));
            _.each(Vis.view.chartRows, function(chartRow, chartRowIndex){
                if (chartRow.datasetIndex == datasetIndex){
                    mindMap.root.children[datasetIndex].children.push(Vis.mindmeister.getChartNode(chartRowIndex));
                }
            });
        });
    } else {
        _.each(Vis.view.chartRows, function(value, chartRowIndex){
            mindMap.root.children.push(Vis.mindmeister.getChartNode(chartRowIndex));
        });
    }

    console.log('mindmap: ');
    console.log(mindMap);
    $('#mm_modal_body').html('');
    return MM.init("9fc50d8e8742c8b163512483b1f839f2", "https://www.mindmeister.com", "mm_modal_body", mindMap);
 }

// Vis.ui
function showAggregateModal(datasetIndex) {
    var dimension, dimensionList, measure, measureList, i, len, results;
    $('#aggregate_modal').modal('show');
    var $aggregate_measures = $('#aggregate_measures').empty();
    var $aggregate_dimensions = $('#aggregate_dimensions').empty();
    $('#aggregate_dimension_error').show();
    $('#aggregate_measure_error').show();
    $('#aggregate_create').prop('disabled', true).off('click').on('click', function(){
        Vis.view.loadingStarted();
        $('#aggregate_modal').modal('hide');
        createAggregatedDataset(datasetIndex, function(datasetInfo){
            var newDataset = new Vis.data.Dataset();
            newDataset.uri = datasetInfo.dataset;
            newDataset.endpoint = datasetInfo.endpoint;
            newDataset.deletedMeasures = [];
            newDataset.isDirty = true;
            Vis.data.datasets.push(newDataset);
            var datasetIndex = Vis.data.datasets.length - 1;
            addNewVisualisation(datasetIndex);
            Vis.view.loadingFinished();
        });
    });
    var sortByLabel = function (a, b) {
        if (a.label.toLowerCase() > b.label.toLowerCase()) {
            return 1;
        }
        if (a.label.toLowerCase() < b.label.toLowerCase()) {
            return -1;
        }
        return 0;
    };
    dimensionList = [];
    for (i = 0; i < Vis.data.datasets[datasetIndex].dimensions.length; i++) {
        dimension = Vis.data.datasets[datasetIndex].dimensions[i];
        dimensionList.push({
            uri: dimension.dimensionuri,
            label: dimension.label
        });
    }
    dimensionList = dimensionList.sort(sortByLabel);
    for (i = 0, len = dimensionList.length; i < len; i++) {
        dimension = dimensionList[i];
        $aggregate_dimensions.append("<div class=\"checkbox\">\n  <label>\n    <input type=\"checkbox\" data-label='" + dimension.label + "' value='" + dimension.uri + "'> " + dimension.label + "\n  </label>\n</div>");
    }
    measureList = [];
    for (i = 0; i < Vis.data.datasets[datasetIndex].measures.length; i++) {
        measure = Vis.data.datasets[datasetIndex].measures[i];
        measureList.push({
            uri: measure.measureuri,
            label: measure.label
        });
    }
    var measure_selector = "<select class=\"form-control input-sm agg_measure\" style=\"width: 80px; display: inline-block;\">";
    results = [];
    for (i = 0, len = measureList.length; i < len; i++) {
        measure = measureList[i];
        measure_selector += "<option value='{\"uri\": \"" + measure.uri + "\", \"label\": \"" + measure.label + "\"}'>" + measure.label + "</option>";
    }
    measure_selector += "</select>";
    $aggregate_measures.append("<div style=\"margin-top: 10px;\">\n  <select class=\"form-control input-sm agg_function\" style=\"width: 80px; display: inline-block;\">\n    <option value='{}'>-</option>\n    <option value='avg'>Average</option>\n    <option value='count'>Count</option>\n    <option value='max'>Maximum</option>\n    <option value='min'>Minimum</option>\n    <option value='sum'>Sum</option>\n  </select> of\n  " + measure_selector + "\n</div>");
    $('#aggregate_more_values').off().on('click', function(e){
        e.preventDefault();
        $aggregate_measures.find('div').first().clone().appendTo($aggregate_measures);
    });
    $aggregate_dimensions.find('input').on('change', function () {
        var checked_dimensions = $('#aggregate_dimensions').find('input:checked').length;
        if ((0 < checked_dimensions && checked_dimensions < Vis.data.datasets[datasetIndex].dimensions.length)) {
            $('#aggregate_dimension_error').hide();
            if (!$('#aggregate_measure_error').is(':visible')) {
                return $('#aggregate_create').prop('disabled', false);
            }
        } else {
            $('#aggregate_dimension_error').show();
            return $('#aggregate_create').prop('disabled', true);
        }
        return "";
    });
    $aggregate_measures.find('select').on('change', function () {
        var selected_measures = $('#aggregate_measures').find('select.agg_function[value!="{}"]').length;
        if (selected_measures > 0) {
            $('#aggregate_measure_error').hide();
            if (!$('#aggregate_dimension_error').is(':visible')) {
                return $('#aggregate_create').prop('disabled', false);
            }
        } else {
            $('#aggregate_measure_error').show();
            return $('#aggregate_create').prop('disabled', true);
        }
        return "";
    });
    return results;
}

// Vis.ui
function createAggregatedDataset(datasetIndex, callback) {
    var grouped_dimensions = [];
    $('#aggregate_dimensions').find('input:checked').each(function () {
        grouped_dimensions.push({
            uri: $(this).val(),
            label: $(this).attr('data-label')
        });
    });
    var aggregated_measures = [];
    $('#aggregate_measures').find('div').each(function () {
        var $div = $(this);
        if ($div.find('select.agg_function[value!="{}"]').length > 0) {
            var aggregated_measure = JSON.parse($div.find('select.agg_measure').first().val());
            aggregated_measure['function'] = $div.find('select.agg_function').first().val();
            aggregated_measures.push(aggregated_measure);
        }
    });
    return $.when($.ajaxQueue({
            url: '/query/aggregate',
            type: 'POST',
            data: JSON.stringify({
                dataset_uri: Vis.data.datasets[datasetIndex].uri,
                endpoint_url: Vis.data.datasets[datasetIndex].endpoint,
                search_type: 'regex',
                grouped_dimensions: grouped_dimensions,
                aggregated_measures: aggregated_measures,
                label: 'Aggregation of: ' + Vis.data.datasets[datasetIndex].datasetName,
                description: '',
                importer: fortytwoId,
                relation: 'Query Wizard',
                source: window.location.href
            })
        })).done(function (data) {
            if (callback){
                callback(data);
            }
        });
}

// Vis.loading
function loadDatasetLabel(datasetIndex) {
    $.ajax({
        url: '/query/get_dataset_label',
        type: 'POST',
        data: JSON.stringify({
            dataset_uri: Vis.data.datasets[datasetIndex].uri,
            endpoint_url: Vis.data.datasets[datasetIndex].endpoint,
            search_type: 'regex'
        })
    }).done(function(data) {
        if (data['dataset']['label']){
            Vis.data.datasets[datasetIndex].datasetName = data['dataset']['label'];
            for(var chartRowIndex=0; chartRowIndex<Vis.view.chartRows.length; chartRowIndex++){
                if (Vis.view.chartRows[chartRowIndex].datasetIndex == datasetIndex){
                    Vis.configuration.setChartObjectCaption(chartRowIndex);
                    Vis.view.setChartRowCaption(chartRowIndex, $getVisRow(chartRowIndex));
                }
            }
        }
    })
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}


// Vis.ui
function addNewDataset(){
    $('#dataset-selection-modal').modal();
    getAndDisplayDatasetsOfSelectedEndpoint();
    //$.ajax({
    //    url: '/query/get42dataDatasets',
    //    type: 'POST',
    //    data: JSON.stringify({
    //        //userId: fortytwoId
    //        userId: 886
    //    })
    //});
}



function getAndDisplayDatasetsOfSelectedEndpoint() {
    $('#dataset_list').empty();
    $('#endpoint_title').html('Loading datasets, please wait …');
    $('#endpoint_datasets_count').html('0 datasets');
    $('#endpoint_description').html('');
    var url = '/query/get_datasets';
    var data = JSON.stringify({
        endpoint_url: $('#dataset_endpoint_selector').val(),
        search_type: 'regex'
      });
    var showOwnDatasets = $('#dataset_endpoint_selector option:selected').data('showowndatasets') == true;
    if (showOwnDatasets){
        url = '/query/get42data_datasets';
        //data = {userId : fortytwoId };
        data = JSON.stringify({
            endpoint_url: $('#dataset_endpoint_selector').val(),
            userId : fortytwoId
      });
    }
    return $.ajax({
      url: url,
      type: 'POST',
      data: data
    }).done(function(data) {
      var dataset, datasetUri, $dataset_li, dataset_size, _i, _len, _ref;
      $('#endpoint_title').html(data.endpoint.label);
      $('#endpoint_description').html('More info at <a href="' + data.endpoint.website_url + '" target="_blank">' + data.endpoint.website_url + '</a>');
      $('#endpoint_datasets_count').html(data.datasets.length + ' datasets');
      _ref = data.datasets;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        dataset = _ref[_i];
        dataset_size = '';
        if (dataset.size > 0) {
          dataset_size = " (" + dataset.size + " entries)";
        }
        datasetUri = encodeURIComponent(dataset.uri);
        $dataset_li = $('<li class=\"list-group-item\"><a href="#"  data-dataset="' + datasetUri + '">'+ dataset.label + '</li>');
        $dataset_li.find('a').on('click', function(e){
            e.preventDefault();
            Vis.chart.addNewDatasetAndChart($('#dataset_endpoint_selector').val(), decodeURIComponent($(this).data('dataset')));
            $('#dataset-selection-modal').modal('hide');
        });
        $('#dataset_list').append($dataset_li);
      }
    });
  }
