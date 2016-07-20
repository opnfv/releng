<?php
	if(isset($_REQUEST['project'])){
	    $selected=$_REQUEST['project'];
	}
	else{
            $url = "http://testresults.opnfv.org:80/test/api/v1/projects";
            $response = file_get_contents($url);
            $data = json_decode($response);
            $projects=$data->projects;
	    $selected=$projects[0]->name;
	}
	$new_url="http://testresults.opnfv.org:80/test/api/v1/projects/".$selected."/cases";
        $response = file_get_contents($new_url);
        $data = json_decode($response);
        $testcases=$data->testcases;
        $i=0;
        $column_str="";
        $column_str=$column_str."<table class=\"table table-striped\"><tr>";
        $column_str=$column_str."<th>#</th><th>Test Case Name</th>";
        $column_str=$column_str."<th>Creation Date</th>";
        $column_str=$column_str."<th>Description</th></tr>";
        foreach ( $testcases as $testcase ){
		$i=$i+1;
	 	$column_str=$column_str."<tr>";
        	$column_str=$column_str."<td>".$i."</td>";
        	$column_str=$column_str."<td>".$testcase->name."</td>";
        	$column_str=$column_str."<td>".$testcase->creation_date."</td>";
        	$column_str=$column_str."<td>".$testcase->description."</td>";
		$column_str=$column_str."</tr>";

    	}
        $column_str=$column_str."</table>";
        echo $column_str;

?>

