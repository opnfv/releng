#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

#export PATH=${PATH}:/root/gsutil

#Step Generate index.html
if [ -f index.html ] ; then
      rm -f index.html
fi

OUTPUT="index.html"

for index in $(gsutil ls -l gs://artifacts.opnfv.org | grep -v logs | grep -v review | awk 'NF==1'| sed s,gs://artifacts.opnfv.org/,,)
do
echo $index
  echo "<LI><a href=\"${index%/*}.html\">"$index"</a></LI>" >> $OUTPUT
done

#functest logs##########################

for project in functest vswitchperf
do

    for index in $(gsutil ls -l gs://artifacts.opnfv.org/logs/"$project"/ |awk 'NF==1'| sed s,gs://artifacts.opnfv.org/,, )
    do
    index="$(echo ${index%/*} | sed s,/,_,g)"
      echo "<LI><a href=\"https://artifacts.opnfv.org/${index%/*}.html\">"$index"</a></LI>" >> $OUTPUT
    done

done
#End step 1
#####################################


#genrate html files for all project except vswitchperf
for index in $(gsutil ls -l gs://artifacts.opnfv.org | grep -v logs |awk 'NF==1'| sed s,gs://artifacts.opnfv.org/,,)
do
OUTPUT=${index%/*}.html
rm -f $OUTPUT


    for filepath in $(gsutil ls -R gs://artifacts.opnfv.org/"$index" | sed s,gs://artifacts.opnfv.org/,, | grep -v "favicon.ico" | grep -v "gsutil" ); do
    echo $filepath

    if [[ $filepath =~ "/:" ]]; then
      path=$(echo $filepath| sed s,/:,,g)
      echo "<UL>" >> $OUTPUT
      echo "<LI>$path</LI>" >> $OUTPUT
      echo "</UL>" >> $OUTPUT
    else
      echo "<LI><a href=\"https://artifacts.opnfv.org/$filepath\">"$filepath"</a></LI>" >> $OUTPUT
    fi
done

gsutil cp $OUTPUT gs://artifacts.opnfv.org/

gsutil -m setmeta \
     -h "Content-Type:text/html" \
     -h "Cache-Control:private, max-age=0, no-transform" \
      gs://artifacts.opnfv.org/$OUTPUT \

done



#generate file for vswitch perf (I dont know what happend here but there is a wierd character in this bucket)

index=vswitchperf
OUTPUT=${index%/*}.html
rm -f $OUTPUT

        for filepath in $(gsutil ls -R gs://artifacts.opnfv.org/"$index" | sed s,gs://artifacts.opnfv.org/,, | grep -v "favicon.ico" | grep -v "gsutil" ); do
        echo $filepath

        if [[ $filepath =~ "/:" ]]; then
          path=$(echo $filepath| sed s,/:,,g)
          echo "<UL>" >> $OUTPUT
          echo "<LI>$path</LI>" >> $OUTPUT
          echo "</UL>" >> $OUTPUT
        else
          echo "<LI><a href=\"https://artifacts.opnfv.org/$filepath\">"$filepath"</a></LI>" >> $OUTPUT
        fi

done


gsutil cp $OUTPUT gs://artifacts.opnfv.org/

gsutil -m setmeta \
     -h "Content-Type:text/html" \
     -h "Cache-Control:private, max-age=0, no-transform" \
      gs://artifacts.opnfv.org/$OUTPUT \

# Gerate html for logs

for project in functest vswitchperf
do
    for index in $(gsutil ls -l gs://artifacts.opnfv.org/logs/"$project"/ |awk 'NF==1'| sed s,gs://artifacts.opnfv.org/,, )
    do

        OUTPUT="$(echo ${index%/*}.html | sed s,/,_,g)"
        echo $OUTPUT
        rm -f $OUTPUT


            for filepath in $(gsutil ls -R gs://artifacts.opnfv.org/"$index" | sed s,gs://artifacts.opnfv.org/,, | grep -v "favicon.ico" | grep -v "gsutil" ); do
            echo $filepath

            if [[ $filepath =~ "/:" ]]; then
              path=$(echo $filepath| sed s,/:,,g)
              echo "<UL>" >> $OUTPUT
              echo "<LI>$path</LI>" >> $OUTPUT
              echo "</UL>" >> $OUTPUT
            else
              echo "<LI><a href=\"https://artifacts.opnfv.org/$filepath\">"$filepath"</a></LI>" >> $OUTPUT
            fi


            done


        gsutil cp $OUTPUT gs://artifacts.opnfv.org/

        gsutil -m setmeta \
             -h "Content-Type:text/html" \
             -h "Cache-Control:private, max-age=0, no-transform" \
              gs://artifacts.opnfv.org/$OUTPUT \


    done
done



OUTPUT="index.html"
echo "<p> Generated on $(date) </p>" >> $OUTPUT

cat <<EOF >> $OUTPUT
<script>
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
ga('create', 'UA-831873-26', 'auto');
ga('send', 'pageview');
</script>
EOF

#copy and uplad index file genrated in first step, last
gsutil cp $OUTPUT gs://artifacts.opnfv.org/

gsutil -m setmeta \
     -h "Content-Type:text/html" \
     -h "Cache-Control:private, max-age=0, no-transform" \
      gs://artifacts.opnfv.org/$OUTPUT \
