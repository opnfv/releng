number=`docker images | awk 'NR != 1' | grep testapi | wc -l`
if [ $number -gt 0 ]; then
    images=`docker images -a | awk 'NR != 1' | grep testapi`
    echo "xxx $images"
    docker images | awk 'NR != 1' | grep testapi | awk '{print $3}' | xargs docker rmi -f &>/dev/null
fi
