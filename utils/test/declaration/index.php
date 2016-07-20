<!DOCTYPE html>
<html lang="en">
<head>
  <title>OPNFV DashBoard</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.2/jquery.min.js"></script>
  <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
<script>
$(function() {

  $('form#new_testcase').on('submit', function(){
    var selected = $('select#sel_pro2').find("option:selected").val();
    var uri = $('input#uri').val();
    var name = $('input#name').val();
    var desc = $('textarea#desc').val();
    var new_url="http://testresults.opnfv.org:80/test/api/v1/projects/"+selected+"/cases";
    $.post("addtestcase.php", {"project":selected,"url":uri,"name":name,"description":desc}, function(result){
        $("div#result").html(result);
});	
});
  
});
$(function() {

  $('select#sel1').on('change', function(){
    var selected = $(this).find("option:selected").val();
    var new_url="http://testresults.opnfv.org:80/test/api/v1/projects/"+selected+"/cases";
    //$.post('testcases.php', {project: selected});
    console.log(selected);
    $.post("testcases.php", {project: selected}, function(result){
        $("div#4a").html(result);
    });

  });
  
});
</script>
<style>
body {
  padding : 10px ;
  
}

#exTab1 .tab-content {
  color : black;
  padding : 5px 15px;
}

#exTab2 h3 {
  color : white;
  background-color: #428bca;
  padding : 5px 15px;
}

/* remove border radius for the tab */

#exTab1 .nav-pills > li > a {
  border-radius: 0;
}

/* change border radius for the tab , apply corners on top*/

#exTab3 .nav-pills > li > a {
  border-radius: 4px 4px 0 0 ;
}

#exTab3 .tab-content {
  color : white;
  background-color: #428bca;
  padding : 5px 15px;
}

</style>
</head>
<body>

<div class="container">
  <h1>OPNFV DASHBOARD: </h1></div>
<div id="exTab1" class="container">
  <ul class="nav nav-pills">
    <li class="active">
      <a href="#1a" data-toggle="tab">PODS</a>
    </li>
    <li><a href="#2a" data-toggle="tab">PROJECTS</a>
    </li>
    <li><a href="#3a" data-toggle="tab">TESTCASES</a>
    </li>
    <li><a href="#5a" data-toggle="tab">ADD TESTCASE</a>
    </li>
    <li><a href="http://testresults.opnfv.org/kibana_dashboards/" >RESULTS</a>
    </li>
  </ul>

  <div class="tab-content clearfix">
    <div class="tab-pane active" id="1a">
	<table class="table table-striped">
	<thead>
    <tr>
      <th>#</th>
      <th>Pod Name</th>
      <th>Creation Date</th>
      <th>Role</th>
      <th>Mode</th>
    </tr>
  </thead>
	<?php
	$url = "http://testresults.opnfv.org:80/test/api/v1/pods";
        $response = file_get_contents($url);
	$data = json_decode($response);
	$pods = $data->pods;
	$i=1;
	foreach ( $pods as $pod ){
	
		$column_str="";
		$column_str="<tr><td>".$i."</td>";
		$column_str=$column_str."<td>".$pod->name."</td>";
		$column_str= $column_str."<td>".$pod->creation_date."</td>";
		$column_str= $column_str."<td>".$pod->role."</td>";
		$column_str= $column_str."<td>".$pod->mode."</td>";
		$column_str= $column_str."</tr>";
		echo $column_str;
		$i=$i+1;
		
	}
	
	?>
	</table>
    </div>
    <div class="tab-pane" id="2a">
 <table class="table table-striped">
        <thead>
    <tr>
      <th>#</th>
      <th>Project</th>
      <th>Creation Date</th>
    </tr>
  </thead>

 <?php
        $url = "http://testresults.opnfv.org:80/test/api/v1/projects";
        $response = file_get_contents($url);
        $data = json_decode($response);
	$projects=$data->projects;
	$i=0;
	foreach ( $projects as $project ){

                $column_str="";
                $column_str="<tr><td>".$i."</td>";
                $column_str=$column_str."<td>".$project->name."</td>";
                $column_str= $column_str."<td>".$project->creation_date."</td>";
                $column_str= $column_str."</tr>";
                echo $column_str;
                $i=$i+1;

        }

?>
	</table>
    </div>
    <div class="tab-pane" id="3a">
<div class="form-group">
  <label for="sel1">Select list:</label>
  <select class="form-control" id="sel1">
<?php
	$url = "http://testresults.opnfv.org:80/test/api/v1/projects";
        $response = file_get_contents($url);
        $data = json_decode($response);
        $projects=$data->projects;
        $i=0;
	$firstvalue=$projects[0]->name;
        foreach ( $projects as $project ){

                $column_str="";
                $column_str="<option>".$project->name."</option>";
                echo $column_str;

        }

?>
</select>


</div>
    <div class="tab-pane" id="4a">
	<?php
		require "testcases.php";
	?>
    </div>
    </div>
    <div class="tab-pane" id="5a">
	<form role="form" id="new_testcase">
<div class="form-group">
  <label for="sel1">Select list:</label>
  <select class="form-control" id="sel_pro2">
<?php
        $url = "http://testresults.opnfv.org:80/test/api/v1/projects";
        $response = file_get_contents($url);
        $data = json_decode($response);
        $projects=$data->projects;
        $i=0;
        $firstvalue=$projects[0]->name;
        foreach ( $projects as $project ){

                $column_str="";
                $column_str="<option>".$project->name."</option>";
                echo $column_str;

        }

?>
</select>


</div>

<div class="form-group"> <!-- Name field -->
		<label class="control-label " for="name">TestCase URI</label>
		<input class="form-control" id="uri" name="uri" type="text"/>
	</div>
<div class="form-group"> <!-- Name field -->
		<label class="control-label " for="name">TestCase Name</label>
		<input class="form-control" id="name" name="name" type="text"/>
	</div>
<div class="form-group"> <!-- Name field -->
		<label class="control-label " for="name">Description</label>
	<textarea class="form-control" rows="5" id="desc"></textarea>
	</div>
  <button type="submit" class="btn btn-default">Submit</button>
</form>
    </div>
<div class="container" id="result"></div>
  </div>
</div>

</body>
</html>
