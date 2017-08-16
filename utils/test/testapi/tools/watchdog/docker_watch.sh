#                                                               *
#    http://www.apache.org/licenses/LICENSE-2.0                 *
#                                                               *
#  Unless required by applicable law or agreed to in writing,   *
#  software distributed under the License is distributed on an  *
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY       *
#  KIND, either express or implied.  See the License for the    *
#  specific language governing permissions and limitations      *
#  under the License.                                           *

# This script checks if deployments are working or and then
# starts the specified containers in case one of the containers
# crash. The only solution is restarting docker as of now.

#!/bin/bash

modules=(testapi reporting)
declare -A urls=( ["testapi"]="http://testresults.opnfv.org/test/swagger/APIs" ["reporting"]="http://testresults.opnfv.org/reporting2/reporting/index.html")

### Functions related to checking.

function check_jobs_status() {
    for module in "${modules[@]}"
    do
        if check_job_status $module; then
            exit 0
        fi
    done
}

function check_job_status() {
    echo -e "Checking job statuses"
    xml=$(curl -m10 "https://build.opnfv.org/ci/job/${1}-automate-master/lastBuild/api/xml?depth=1")
    building=$(grep -oPm1 "(?<=<building>)[^<]+" <<< "$xml")
    if [ $building == 'false' ]
    then
        return 1
    else
        return 0
    fi
}

function check_connection() {
    echo "Checking $1 connection : $2"
    cmd=`curl --head -m10 --request GET ${2} | grep '200 OK' > /dev/null`
    rc=$?
    if [[ $rc == 0 ]]; then
        return 0
    else
        return 1
    fi
}

function check_modules() {
    failed_modules=()
    for module in "${modules[@]}"
    do
        if ! check_connection $module "${urls[$module]}"; then
        echo -e "$module failed"
            failed_modules+=($module)
        fi
    done
    echo $failed_modules
    if [ ! -z "$failed_modules" ]; then
        return 1
    else
        echo -e "All modules working good"
        exit 0
    fi
}


### Functions related fixes.

function restart_docker() {
    echo -e "Restarting docker"
    sudo service docker restart
}

function start_container() {
    echo -e "Starting a container $1"
    sudo docker start $1
    sleep 5
    if ! check_connection $1 "${urls[$1]}"; then
        echo -e "Starting an old container $1_old"
        sudo docker start $1"_old"
        sleep 5
    fi
}

function run_fix_two() {
    check_jobs_status
    restart_docker
    run_fix_one $modules
}

function run_fix_one() {
    for module in $1
    do
        start_container $module
    done
}

### Checking conditions and running appropriate fixes.

echo -e
echo -e "WatchDog Started"
echo -e
echo -e `date "+%Y-%m-%d %H:%M:%S.%N"`
echo -e 

if ! check_modules; then
    echo -e "Running fix level one"
    run_fix_one $failed_modules
fi

if ! check_modules; then
    echo -e "Running fix level two"
    run_fix_two
fi

if ! check_modules; then
   echo "WatchDog Failed"
fi

sudo docker ps
sudo docker images