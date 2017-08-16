#!/bin/bash

#                                                               *
#    http://www.apache.org/licenses/LICENSE-2.0                 *
#                                                               *
#  Unless required by applicable law or agreed to in writing,   *
#  software distributed under the License is distributed on an  *
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY       *
#  KIND, either express or implied.  See the License for the    *
#  specific language governing permissions and limitations      *
#  under the License.        					*

# This script checks if deployments are working or and then 
# starts the specified containers in case one of the containers 
# crash. The only solution is restarting docker as of now.


modules=(testapi reporting)
declare -A urls=( ["testapi"]="http://testresults.opnfv.org/test/swagger/APIs" ["reporting"]="http://testresults.opnfv.org/reporting2/reporting/index.html")

function check_job_status() {
    echo "Checking job statuses"
    xml=$(curl -m10 "https://build.opnfv.org/ci/job/${1}-automate-master/lastBuild/api/xml?depth=1")
    building=$(grep -oPm1 "(?<=<building>)[^<]+" <<< "$xml")
    if [ $building == 'false' ]
    then
	return 1
    else
	return 0
    fi
}

function restart_docker() {
    sudo service docker restart
}

function remove_container() {
    sudo docker rm -f $1
}

function start_testapi_container() {
    sudo docker run -dti --name testapi -p 8082:8000 -e mongodb_url=mongodb://172.17.0.1:27017 \
        -e base_url=http://testresults.opnfv.org/test rohitsakala/testapi
}

function start_reporting_container() {
    sudo docker run -itd --name reporting -p 8084:8000 rohitsakala/reporting
}

function check_connection() {
    echo "Checking $1 connection : $2"
    cmd=`curl --head -m10 --request GET ${2} | grep '200 OK' > /dev/null`
    rc=$?
    echo $rc
    if [[ $rc == 0 ]]; then
        return 0
    else
        return 1
    fi
}

function check_jobs_status() {
    for module in "${modules[@]}"
    do
        if check_job_status $module; then
	    exit 0
	fi
    done
}

function run_fix() {
    check_jobs_status
    for i in "${modules[@]}"
    do
        remove_container $i
    done
    restart_docker
    start_testapi_container
    start_reporting_container
}


for module in "${modules[@]}"
do
    if ! check_connection $module "${urls[$module]}"; then
        run_fix
	break
    fi
done
	
sudo docker ps
sudo docker images
