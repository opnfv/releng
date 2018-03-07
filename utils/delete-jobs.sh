#!/bin/bash
main () {

echo -n "Enter username: "
read -r username
echo -n "Enter api_token: "
read -r password

echo "$username:$password"

if [[ -e "$file_of_jobs_to_delete" ]]; then

  for job in $(cat "$file_of_jobs_to_delete"); do 
    if [[ $test_mode == true ]]; then
      echo "TEST MODE! curl -X POST "https://$username:$password@build.opnfv.org/ci/job/${job}/doDelete""
    else
      echo "RUNNING! curl -X POST "https://$username:$password@build.opnfv.org/ci/job/${job}/doDelete""
      curl -X POST "https://$username:$password@build.opnfv.org/ci/job/${job}/doDelete"
    fi
   done

else

  wget -O jenkins-jobs.xml "https://build.opnfv.org/ci/api/xml"
  
  jobs=$(xmlstarlet sel -t -m '//hudson/job' \
         -n -v 'name' jenkins-jobs.xml | \
         grep "$search_string")
  
  for job in $(echo "$jobs" | tr "\n" " "); do
    if [[ $test_mode == true ]]; then
      echo "TEST MODE ONLY! curl -X POST "https://$username:$password@build.opnfv.org/ci/job/${job}/doDelete""
    else
      echo "RUNNING! curl -X POST "https://$username:$password@build.opnfv.org/ci/job/${job}/doDelete""
      curl -X POST "https://$username:$password@build.opnfv.org/ci/job/${job}/doDelete"
    fi
  done

fi

}

usage() {
    cat << EOF

# Script to delete Jenkins jobs by searching a string.
#
#   Usage: ./$0 -d <search_string>
#   Usage: ./$0 -j file-with-list-of-jobs-to-delete
#
#
# For example: *-validate-autorelease-*
#     ./delete-jobs -d validate-autorelease
#
# Please run with -t first to test what would be deleted!

usage: $0 [OPTIONS]
 -h  show this message
 -j  choose file containing list of jenkins jobs to delete
 -d  delete via <search_string>
 -t  test, show what would be run with echo. 

EOF

    exit 1
}



if [[ -z "$@" ]]; then
   usage
fi

while getopts "hj:d:t" OPTION
do
    case $OPTION in
        h ) usage ;;
        j ) file_of_jobs_to_delete="$OPTARG" ;;
        d ) search_string="$OPTARG" ;;
        t ) test_mode=true ;;
        \? ) echo "Unknown option: -$OPTARG" >&2; exit 1;;
    esac
done

main "$@"
