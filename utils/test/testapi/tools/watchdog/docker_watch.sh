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
declare -A ports=( ["testapi"]="8082" ["reporting"]="8084")
declare -A urls=( ["testapi"]="http://localhost:8082" ["reporting"]="http://testresults.opnfv.org/reporting2/reporting/index.html")


### Functions related to checking.

function check_jobs_status() {
    echo -e "Checking job statuses"
    for module in "${modules[@]}"
    do
        if check_job_status $module; then
            exit 0
        fi
    done
}

function check_job_status() {
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
    if [ ! -z "$failed_modules" ]; then
        echo -e "Failed Modules: $failed_modules"
        return 1
    else
        echo -e "All modules working good"
        exit 0
    fi
}

### Functions related fixes.

function docker_proxy_fix() {
    for module in $1
    do
        echo -e "Kill docker proxy and restart containers"
        pid=$(sudo netstat -nlp | grep :${ports[$module]} | awk '{print $7}' | cut -d'/' -f1)
        if [ ! -z "$pid" ]; then
            sudo kill $pid
            start_container $module
        else
            echo "Not a docker proxy bind issue. Some other issue"
        fi
    done
}

function start_container() {
    echo -e "Starting a container $1"
    sudo docker stop $1
    sudo docker start $1
    sleep 5
    if ! check_connection $1 "${urls[$1]}"; then
        echo -e "Starting an old container $1_old"
        sudo docker stop $1
        sudo docker start $1"_old"
        sleep 5
    fi
}

function run_fix_two() {
    check_jobs_status
    docker_proxy_fix $1
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
    run_fix_two $failed_modules
fi

if ! check_modules; then
   echo "WatchDog Failed"
fi

sudo docker ps
sudo docker images