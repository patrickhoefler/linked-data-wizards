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

var dataUrlBase = "/viz?cmd=getD3Data";
var dataUrl;

var globals={
	     cachedChart:"",
	     cachedDimension: "",
	     mappingArray : [],
	     chartArray : [],
	     dimensionArray : [],
	     dataset : "",
	     switchArray: []
	     };

$(document).ready(function () {
    $.address.externalChange(external_address_change_handler); // Sobald sich die adresse ändert wird die fkt external_address_change_handler aufgerufen
    $("#selectable3").selectable({
    	stop: function(){
            $(".ui-selected", this).each(function(){
            	globals.cachedChart= this.id;
            	/*if (globals.mappingArray.length == 1){
            		globals.cachedChart = "";
            		getVisualization (globals.cachedChart, decodeURIComponent(globals.dataset));
            
            	}*/
            
            
            });
        },
     selecting:function() {
    	$(".ui-selected", this).each(function(){
    	$(this).toggleClass("ui-selected");
    	});
      }
    });

   /*$("#selectable1").selectable({
    	stop: function(){
            $(".ui-selected", this).each(function(){
            	var cachedDimension = this.id;
            	var dimensionUri = $(this).attr("dimensionuri");
            	var mappingObject = {'dim':cachedDimension , 'dimensionuri':dimensionUri};
            	globals.mappingArray.push(mappingObject);
            	console.log (globals.mappingArray);
            });
        },*/

    $("#selectable1").selectable({
    	stop: function(){
            $(".ui-selected", this).each(function(){
            	var cachedDimension = this.id;
            	var dimensionUri = $(this).attr("dimensionuri");
            	console.log(globals.dimensionArray);
            	selectDim(cachedDimension, dimensionUri);

            });


    	 },

     selecting:function() {
    	$(".ui-selected", this).each(function(){
    	$(this).toggleClass("ui-selected");
    	});
      }
    });
    $("#preview").button();

    $("#preview").click(
    		function(){
    			getVisualization(globals.cachedChart, decodeURIComponent(globals.dataset));
    
    
    		}
    		);
    $("#switch").button();

    $("#switch").click(
    		function(){
    
    			switchDimension();
    

    
    
    		}
    		);


});



function external_address_change_handler(event){
    var value, dataset, chart, chartid;
    if (event.parameterNames.length > 0) {
        $('#vis').html('');
        $("#demo2").html('');
        $("#demo2Up").html('');
        $("#selectable3").html('');
        $("#selectable1").html('');




        for (key in event.parameters) {
            value = event.parameters[key];
            if (key == "dataset"){
                globals.dataset = value;
            }
        }
        if (dataset == ""){
            alert('Parameter list not correct');
            return;
        }

      getPreview();
    }
}




function selectDim(cachedDimension, dimensionUri){
	globals.mappingArray = [];

	var mappingObject = {'dim':cachedDimension , 'dimensionuri':dimensionUri};
	globals.mappingArray.push(mappingObject);
	//console.log(globals.dimensionArray);
	if (globals.cachedChart == "parallelcoordinates"){
		for (var i = 0; i<globals.dimensionArray.length;i++){

			var lab = globals.dimensionArray[i].label;
			var dimensionUri = globals.dimensionArray[i].dimensionuri;
			if (lab != cachedDimension){
				var mappingObject2 = {'dim':lab,'dimensionuri':dimensionUri };
				globals.mappingArray.push(mappingObject2);
				//console.log(globals.mappingArray);
			}

		}

	}


	//console.log(globals.mappingArray);
	//globals.mappingArray = [];
}

function getPreview (){
    var start=null;
    globals.chartArray = [];
    console.log(decodeURIComponent(globals.dataset));
    $.post("/viz", { cmd: "getPreviewAuto", chart:'', dataset:decodeURIComponent(globals.dataset), dimension:''},
        function(dt) {
            var charts="";
            $("#vis").html("");
            $("#demo2").html('');
            $("#demo2Up").html('');
            $("#selectable3").html('');

            for(var x = 0; x < dt.length; x++){
            	var ch = dt[x];
            	console.log (ch);
            	globals.chartArray.push(ch);
            	//alert(ch);
                charts = charts+'<li id='+ch+' class="ui-widget-content">'+ch+'</li>';
                getDimensions();

            }
			$("#selectable3").html(charts);
    }, "json").error(function() {err("Error while showing supported charts."); });


    }
function getDimensions (){
	$.post("/viz", { cmd: "getDimension",  dataset:decodeURIComponent(globals.dataset)},
	        function(dt) {
			globals.dimensionArray= dt;
			globals.mappingArray = [];
			globals.cachedChart = "";
			globals.switchArray = [];

	            $("#vis").html("");
	            var dimensions = "";
	            for(var x = 0; x < dt.length; x++){
	            	console.log (dt);
	                var dimension = dt[x].label;
	                var dimensionuri = dt[x].dimensionuri;
	                globals.switchArray = dt;
	                //dimensions = dimensions+'<li id='+dimension+'dimensionuri='+dimensionuri+'class="ui-widget-content">'+dimension+'</li>';
	                if(dt.length != 1){
	                	dimensions = dimensions+'<li id="'+dimension+'" dimensionuri="'+dimensionuri+'" class="ui-widget-content">'+dimension+'</li>';
	                
	                }
	                if(dimension==null){
	                    alert("Dimension can not be showed");
	                    return;
	                }

	            }
	            if(dt.length == 1){
	            	var chart = "";
                	var mappingObject = {'dim':dimension , 'dimensionuri':dimensionuri};
                	globals.mappingArray.push(mappingObject);

            		chart = globals.chartArray [0];
            		console.log (chart);
            		getVisualization(chart);
              }
	            $("#selectable1").html(dimensions);
	        }, "json")
	        .error(function() {alert("Error while loading dimensions."); });
	}

function getVisualization (cachedChart){
	 var start=null;
	 console.log (cachedChart);
	   $("#vis").html("<img src='/static/images/ajax-loader.gif' border='0'>");
	    $.post("/viz", { cmd: "getVisualization", chart:cachedChart, dataset:decodeURIComponent(globals.dataset), dimension:JSON.stringify(globals.mappingArray)},
	    
	        function(dt) {
	            var conf =  'var config={location:"vis", height:"600", width:"700", title:"Generated chart"}';
	            var warn = null;
	            $("#vis").html("");

	            for(var x = 0; x < dt.length; x++){
	            
	                start = dt[x].start;
	                if(start==null){
	                    alert("Chart  could not be generated");
	                    return;
	                }

	                eval(conf);
	                eval(start);

	                if (globals.mappingArray.length != 1){
	                globals.mappingArray = [];
	                }

	            }


	        }, "json")
	        .error(function() {alert("Error while preparing preview."); });
	}

function switchDimension(){

	var i = 0;
	var dimensions = "";
	var newArray = [];
	//console.log(globals.switchArray);
	for (i= (globals.switchArray.length)-1;i>=0; i--){
		var dimension = globals.switchArray[i].label;
        var dimensionuri = globals.switchArray[i].dimensionuri;
        dimensions = dimensions+'<li id="'+dimension+'" dimensionuri="'+dimensionuri+'" class="ui-widget-content">'+dimension+'</li>';
        var newObject = {'dimensionuri':dimensionuri, 'label': dimension };
        newArray .push(newObject);

	}
	globals.switchArray = newArray;
	$("#selectable1").html(dimensions);


}



