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

## List of modules
modules=(testapi reporting)

## Ports of the modules
declare -A ports=( ["testapi"]="8082" ["reporting"]="8084")

## Urls to check if the modules are deployed or not ?
declare -A urls=( ["testapi"]="http://testresults.opnfv.org/test/" \
    ["reporting"]="http://testresults.opnfv.org/reporting/index.html")

### Functions related to checking.

function is_deploying() {
    xml=$(curl -m10 "https://build.opnfv.org/ci/job/${1}-automate-master/lastBuild/api/xml?depth=1")
    building=$(grep -oPm1 "(?<=<building>)[^<]+" <<< "$xml")
    if [[ $building == "false" ]]
    then
        false
    else
        true
    fi
}

function get_docker_status() {
    status=$(service docker status | sed -n 3p | cut -d ' ' -f5)
    echo -e "Docker status: $status"
    if [ $status = "active" ]
    then
        true
    else
        false
    fi
}

function check_connectivity() {
    echo "Checking $1 connection : $2"
    cmd=`curl --head -m10 --request GET ${2} | grep '200 OK' > /dev/null`
    rc=$?
    if [[ $rc == 0 ]]; then
        true
    else
        false
    fi
}

function check_modules() {
    echo -e "Checking modules"
    failed_modules=()
    for module in "${modules[@]}"
    do
        if is_deploying $module; then
            continue
        fi
        if ! check_connectivity $module "${urls[$module]}"; then
            echo -e "$module failed"
            failed_modules+=($module)
        fi
    done
    if [ ! -z "$failed_modules" ]; then
        echo -e "Failed Modules: $failed_modules"
        false
    else
        echo -e "All modules working good"
        exit 0
    fi
}

### Functions related fixes.

function restart_docker_fix() {
    echo -e "Running restart_docker_fix"
    service docker restart
    start_containers_fix "${modules[@]}"
}

function docker_proxy_fix() {
    echo -e "Running docker_proxy_fix"
    fix_modules=("${@}")
    for module in "${fix_modules[@]}"
    do
        echo -e "Kill docker proxy and restart containers"
        pid=$(netstat -nlp | grep :${ports[$module]} | awk '{print $7}' | cut -d'/' -f1)
        echo $pid
        if [ ! -z "$pid" ]; then
            kill $pid
            start_container_fix $module
        fi
    done
}

function start_containers_fix() {
    start_modules=("${@}")
    for module in "${start_modules[@]}"
    do
        start_container_fix $module
    done
}

function start_container_fix() {
    echo -e "Starting a container $module"
    sudo docker stop $module
    sudo docker start $module
    sleep 5
    if ! check_connectivity $module "${urls[$module]}"; then
        echo -e "Starting an old container $module_old"
        sudo docker stop $module
        sudo docker start $module"_old"
        sleep 5
    fi
}

### Main Flow

echo -e
echo -e "WatchDog Started"
echo -e
echo -e `date "+%Y-%m-%d %H:%M:%S.%N"`
echo -e

## If the problem is related to docker daemon

if ! get_docker_status; then
    restart_docker_fix
    if ! check_modules; then
        echo -e "Watchdog failed while restart_docker_fix"
    fi
    exit
fi

## If the problem is related to docker proxy

if ! check_modules; then
    docker_proxy_fix "${failed_modules[@]}"
fi

## If any other problem : restart docker

if ! check_modules; then
    restart_docker_fix
fi

## If nothing works out

if ! check_modules; then
    echo -e "Watchdog failed"
fi

sudo docker ps
sudo docker images