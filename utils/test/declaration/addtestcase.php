<?php
function sendPostData($url, $post){
  $ch = curl_init($url);
  $headers= array('Accept: application/json','Content-Type: application/json');
  curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
  curl_setopt($ch, CURLOPT_POSTFIELDS,$post);
  curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
  $result = curl_exec($ch);
  curl_close($ch);
  return $result;
}

if(isset($_REQUEST['url'])){
   $url=$_REQUEST['url'];
}
if(isset($_REQUEST['name'])){
   $name=$_REQUEST['name'];
}
if(isset($_REQUEST['desc'])){
   $desc=$_REQUEST['desc'];
}
if(isset($_REQUEST['project'])){

   $url_send=$_REQUEST['project'];
   $url_send="http://testresults.opnfv.org:80/test/api/v1/projects/".$url_send."/cases";
   $str_data=array('url'=>$url,'name'=>$name,'description'=>$desc);
   $str_data=json_encode($str_data);
   $res=sendPostData($url_send, $str_data);
   echo '<div class="alert alert-success"> <strong>Success!</strong> Added New test Case  </div>';

}else{

   echo '<div class="alert alert-danger"> <strong>Error!</strong> Failed to Add New test Case  </div>';

}

?>

