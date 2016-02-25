/*#############################################################################
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
*/

// Function to format date according to JS
function format_date(inputDate){
    var input = inputDate.slice(0,-7);
    input=input.replace(' ','T');
    input+='Z';
    return new Date(Date.parse(input));
}

// Draw a single graph for a specific test for a specific installer
function draw_graph_per_scenario_per_installer (filename, installer, pod, scenario, test_unit){
    $.getJSON(filename, function(data) {
    var serie = [];
    index_test = 0;
    // find index mapping to the test_unit
    for (var i=0; i<data.dashboard.length; i++)
        if (data.dashboard[i].name==test_unit){
           index_test=i;
           break;
        }

    // build the data according to dygraph
    for (i=0; i<data.dashboard[index_test].data_set.length; i++) {
        var d = [];
        result = data.dashboard[index_test].data_set[i];
        d.push(format_date(result.x));

        // push y data if available
        var keys = Object.keys(result);
        for (var y in opnfv_dashboard_ys)
           if ($.inArray(opnfv_dashboard_ys[y], keys)!=-1) d.push(result[opnfv_dashboard_ys[y]]);
               serie.push(d);
    };

    // sort by date/time
    serie.sort(function(a,b){
        return new Date(a[0]).getTime()-new Date(b[0]).getTime()
    });

    // Label management
    var yLabel = '';
    if (test_unit.includes('nb'))
        yLabel = 'number';
    else if (test_unit.includes('duration'))
        yLabel = 'seconds';
    var labels = [];
    labels.push('time');
    var keys = Object.keys(data.dashboard[index_test].info);
    for (var y in opnfv_dashboard_y_labels)
        if ($.inArray(opnfv_dashboard_y_labels[y], keys)!=-1) labels.push(data.dashboard[index_test].info[opnfv_dashboard_y_labels[y]]);

    // Draw the graph
    g = new Dygraph(
        document.getElementById(scenario),
        serie,
        {
            colors: [opnfv_dashboard_graph_color_ok, opnfv_dashboard_graph_color_nok, opnfv_dashboard_graph_color_other],
            fillGraph: true,
            legend: opnfv_dashboard_graph_legend,
            title: scenario,
            titleHeight: opnfv_dashboard_graph_title_height,
            ylabel: yLabel,
            labelsDivStyles: {
                'text-align': opnfv_dashboard_graph_text_align,
                'background-color': opnfv_dashboard_graph_background_color
            },
            axisLabelColor: opnfv_dashboard_graph_axis_label_color,
            labels: labels,
            highlightSeriesOpts: {strokeWidth: opnfv_dashboard_graph_stroke_width},
            stepPlot: true
        }
    );
});
}

// function to generate all the graphs for all installers
function draw_graphs_all_scenarios_per_installer () {
    installer = opnfv_dashboard_installer;
    project = opnfv_dashboard_project;
    test = opnfv_dashboard_test;
    test_unit = opnfv_dashboard_test_unit;
    for (i=0; i<opnfv_dashboard_installers_scenarios[installer].length; i++){
        var filename = './' + opnfv_dashboard_file_directory + '/' + installer + '/' + project + '/' + opnfv_dashboard_file_prefix + project+'_'+test+'_'+opnfv_dashboard_installers_scenarios[installer][i];
        if (opnfv_dashboard_pod!='all')
            filename += '_' + opnfv_dashboard_pod;
        filename += opnfv_dashboard_file_suffix;
        console.log(filename);
        draw_graph_per_scenario_per_installer(filename, installer, opnfv_dashboard_pod, opnfv_dashboard_installers_scenarios[installer][i], test_unit);
    }
}

function on_testcase_draw_graph(test, test_unit){
    opnfv_dashboard_test = test;
    opnfv_dashboard_test_unit = test_unit;
    show_divs(opnfv_dashboard_installer);
    draw_graphs_all_scenarios_per_installer();
    $("#testcase_selected").html(test_unit);
}

function on_installer_draw_graph(installer){
   opnfv_dashboard_installer = installer;
   show_installers(installer);
   opnfv_dashboard_pod = 'all';  // force the new pod to 'all' because there is # pods per installer
   show_installers_pods(opnfv_dashboard_pod);
   show_divs(installer);
   draw_graphs_all_scenarios_per_installer ();
}

function on_pod_draw_graph(pod){
   opnfv_dashboard_pod = pod;
   show_installers_pods(pod);
   show_divs(opnfv_dashboard_installer);
   draw_graphs_all_scenarios_per_installer ();
}

function on_ready_draw_graph(){
   opnfv_dashboard_test = 'vPing';
   opnfv_dashboard_test_unit = 'vPing duration';
   opnfv_dashboard_installer = opnfv_dashboard_installers[Math.round((Math.random(opnfv_dashboard_installers.length-1)))];
   show_installers_pods(opnfv_dashboard_installers_pods[opnfv_dashboard_installer][0]);
   show_installers(opnfv_dashboard_installer);
   show_divs(opnfv_dashboard_installer);
   $("#testcase_selected").html(opnfv_dashboard_test_unit);
   draw_graphs_all_scenarios_per_installer ();
}

// generate test case selection
function show_testcases(){
    var html_testcases = '<button class="btn btn-default dropdown-toggle" type="button" data-toggle="dropdown">Select a test case';
    html_testcases += '<span class="caret"></span></button>';
    html_testcases += '<ul class="dropdown-menu">';

    var family_testcases = Object.keys(opnfv_dashboard_testcases)
    for (var i in family_testcases){
        html_testcases += '<li class="dropdown-header">' + family_testcases[i] + '</li>';
        var testcase = family_testcases[i];
        family_tests = Object.keys(opnfv_dashboard_testcases[testcase]);
        for (var j in family_tests){
            var test = family_tests[j];
            family_tests_units = Object.keys(opnfv_dashboard_testcases[testcase][test]);
            for (var k in family_tests_units){
                test_unit = opnfv_dashboard_testcases[testcase][test][k];
                html_testcases += '<li><a href="#"  onClick="on_testcase_draw_graph(\''+ test +'\',\''+test_unit +'\')">' + opnfv_dashboard_testcases[testcase][test][k] + '</a></li>';
            }
        }
    }
    html_testcases+='</ul>';
    $("#testcase").html(html_testcases);
}

// generate installers buttons
function show_installers(active_installer)
{
    var html_installers = '';
    html_installers += '<ul class="nav nav-pills">';
    for (var i in opnfv_dashboard_installers)
        if (opnfv_dashboard_installers[i]==active_installer)
            html_installers += '<li class="active"><a href="#" onClick="on_installer_draw_graph(\''+opnfv_dashboard_installers[i]+'\')">'+opnfv_dashboard_installers[i]+'</a></li>';         
        else
            html_installers += '<li><a href="#" onClick="on_installer_draw_graph(\''+opnfv_dashboard_installers[i]+'\')">'+opnfv_dashboard_installers[i]+'</a></li>';
    html_installers += '</ul>';
    $("#installers").html(html_installers);
}

// generate pods buttons
function show_installers_pods(active_pod)
{
    var html_pods = '';
    html_pods += '<ul class="nav nav-pills">';
    for (var i in opnfv_dashboard_installers_pods[opnfv_dashboard_installer])
        if (opnfv_dashboard_installers_pods[opnfv_dashboard_installer][i]==active_pod)
            html_pods += '<li class="active"><a href="#" onClick="on_pod_draw_graph(\''+opnfv_dashboard_installers_pods[opnfv_dashboard_installer][i]+'\')">'+opnfv_dashboard_installers_pods_print[opnfv_dashboard_installer][i]+'</a></li>';         
        else
            html_pods += '<li><a href="#" onClick="on_pod_draw_graph(\''+opnfv_dashboard_installers_pods[opnfv_dashboard_installer][i]+'\')">'+opnfv_dashboard_installers_pods_print[opnfv_dashboard_installer][i]+'</a></li>';
    html_pods += '</ul>';
    $("#pods").html(html_pods);
}

// generate a div per installer (to host the graph)
function show_divs(installer){
  $("#graphs").remove();
  $("body").append('<div id="graphs">');
  for (var i in opnfv_dashboard_installers_scenarios[installer]){
    var div_scenario = '<div class= "chart" id="' + opnfv_dashboard_installers_scenarios[installer][i] + '"/>';
console.log(div_scenario);
    var $newdiv = $(div_scenario);
    $("#graphs").append($newdiv);
  }
}

// generate HTML menus and buttons
$( document ).ready(function(){
  console.log( "ready!" );
  
  //show_installers('');
  show_testcases();
  on_ready_draw_graph();
});
