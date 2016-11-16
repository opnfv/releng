#!/bin/bash
cd ..

export PYTHONPATH="${PYTHONPATH}:."
export CONFIG_REPORTING_YAML=./reporting.yaml

declare -a versions=(colorado master)
declare -a projects=(functest yardstick)

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
# yardstick |

if [ -z "$1" ]; then
  echo "********************************"
  echo " Functest reporting " 
  echo "********************************"
  echo "reporting vIMS..."
  python ./functest/reporting-vims.py
  echo "reporting vIMS...OK"
  sleep 10
  echo "reporting Tempest..."
  python ./functest/reporting-tempest.py
  echo "reporting Tempest...OK"
  sleep 10
  echo "reporting status..."
  python ./functest/reporting-status.py
  echo "Functest reporting status...OK"

  echo "********************************"
  echo " Yardstick reporting " 
  echo "********************************"
  python ./yardstick/reporting-status.py
  echo "Yardstick reporting status...OK"
else
  if [ -z "$2" ]; then
    reporting_type="status"
  fi
  echo "********************************"
  echo " $project/$reporting_type reporting " 
  echo "********************************"
  python ./$project/reporting-$reporting_type.py
fi

