#!/bin/bash

export PYTHONPATH="${PYTHONPATH}:./reporting"
export CONFIG_REPORTING_YAML=./reporting/reporting.yaml

declare -a versions=(danube master)
declare -a projects=(functest storperf yardstick qtip)

project=$1
reporting_type=$2

# create Directories if needed
for i in "${versions[@]}"
do
    for j in "${projects[@]}"
       do
           mkdir -p display/$i/$j
       done
done

# copy images, js, css, 3rd_party
cp -Rf 3rd_party display
cp -Rf css display
cp -Rf html/* display
cp -Rf img display
cp -Rf js display

# if nothing is precised run all the reporting generation
#  projet   |        option
#   $1      |          $2
# functest  | status, vims, tempest
# yardstick | status
# storperf  | status
# qtip      | status

function report_project()
{
  project=$1
  dir=$2
  type=$3
  echo "********************************"
  echo " $project reporting "
  echo "********************************"
  python ./reporting/$dir/reporting-$type.py
  if [ $? ]; then
    echo "$project reporting $type...OK"
  else
    echo "$project reporting $type...KO"
  fi
}

if [ -z "$1" ]; then
  echo "********************************"
  echo " * Static status reporting     *"
  echo "********************************"
  for i in "${projects[@]}"
  do
    report_project $i $i "status"
    sleep 5
  done
  report_project "QTIP" "qtip" "status"


  echo "Functest reporting vIMS..."
  report_project "functest" "functest" "vims"
  echo "reporting vIMS...OK"
  sleep 5
  echo "Functest reporting Tempest..."
  report_project "functest" "functest" "tempest"
  echo "reporting Tempest...OK"
  sleep 5

else
  if [ -z "$2" ]; then
    reporting_type="status"
  fi
  report_project $project $project $reporting_type
fi
