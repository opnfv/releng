/*#############################################################################
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
*/

// Function to sort data to be ordered according to the time
function sortFunction(a,b){
    var dateA = new Date(a.date).getTime();
    var dateB = new Date(b.date).getTime();
    return dateA > dateB ? 1 : -1;
};

// Function to format date according to JS
function formatDate(inputDate){
    var input=inputDate.slice(0,-7);
    input=input.replace(' ','T');
    input+='Z';
    return new Date(Date.parse(input));
}

// Draw a single graph for a specific test for a specific installer
function drawGraph(filename,installer,test_unit){
    $.getJSON( filename, function(data) {
    var serie=[];
    index_test=0;
    // find index mapping to the test_unit
    for (var i=0;i<data.dashboard.length;i++)
       if (data.dashboard[i].name==test_unit){index_test=i; break;}

    // build the data according to dygraph
    for (i=0;i<data.dashboard[index_test].data_set.length;i++) {
        var d=[];
        result=data.dashboard[index_test].data_set[i];
        d.push(formatDate(result.x));

        // push y data if available
        var keys=Object.keys(result);
        for (var y in opnfv_dashboard_ys)
            if ($.inArray(opnfv_dashboard_ys[y], keys)!=-1) d.push(result[opnfv_dashboard_ys[y]]); 	
                serie.push(d);
    };

    // sort by date/time
    serie.sort(function(a,b){
        return new Date(a[0]).getTime()-new Date(b[0]).getTime()
    });

    // Label management
    var yLabel='';
    if (test_unit.includes('nb'))
        yLabel='number';
    else if (test_unit.includes('duration'))
        yLabel='seconds';
    var labels=[];
    labels.push('time');
    var keys=Object.keys(data.dashboard[index_test].info);
    for (var y in opnfv_dashboard_y_labels)
        if ($.inArray(opnfv_dashboard_y_labels[y], keys)!=-1) labels.push(data.dashboard[index_test].info[opnfv_dashboard_y_labels[y]]); 	

    // Draw the graph
    g=new Dygraph(
        document.getElementById(installer),
        serie,
        {
            colors:[opnfv_dashboard_graph_color_ok, opnfv_dashboard_graph_color_nok, opnfv_dashboard_graph_color_other],
            fillGraph:true,
            legend:opnfv_dashboard_graph_legend,
            title:installer,
            titleHeight:opnfv_dashboard_graph_title_height,
            ylabel:yLabel,
            labelsDivStyles:{
                'text-align': opnfv_dashboard_graph_text_align,
                'background-color': opnfv_dashboard_graph_background_color
            },
            axisLabelColor:opnfv_dashboard_graph_axis_label_color,
            labels:labels,
            highlightSeriesOpts:{strokeWidth:opnfv_dashboard_graph_stroke_width},
            stepPlot:true
        }
    );
});
}

// function to generate all the graphs for all installers
function drawGraphsSerie(project,test,test_unit) {
    for (i=0;i<opnfv_dashboard_installers.length;i++){
        var filename='./'+opnfv_dashboard_file_directory+'/'+project+'/'+opnfv_dashboard_file_prefix+project+'_'+test+'_'+opnfv_dashboard_installers[i]+opnfv_dashboard_file_suffix;
        drawGraph(filename,opnfv_dashboard_installers[i],test_unit);
    }
}

// generate text and buttons for each test and unit test
var text_html='';
for (var i in opnfv_dashboard_projects)
    for (var project in opnfv_dashboard_projects[i])
        for (var test in opnfv_dashboard_projects[i][project]){
            text_html+=test+' ';
            for (var t in  opnfv_dashboard_projects[i][project][test]){
                test_unit=opnfv_dashboard_projects[i][project][test][t];
                text_html+='<button onClick="drawGraphsSerie(\''+project+'\',\''+test +'\',\''+test_unit+'\')">'+test_unit+'</button>';
            }
            text_html+='<br>';
        }
document.getElementById('tests').innerHTML=text_html;

// debug
console.log(text_html);

// generate a div per installer (to host the graph)
for (var i in opnfv_dashboard_installers){
    var div_installer='<div class= "chart" id="'+opnfv_dashboard_installers[i]+'"/>'
    var $newdiv=$(div_installer);
    $("body").append($newdiv);
}
