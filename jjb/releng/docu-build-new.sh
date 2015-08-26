#!/bin/bash 

clean() {{
if [[ -d docs/output ]]; then
rm -rf docs/output
echo "cleaning up output directory"
fi
}} 

trap clean EXIT TERM INT SIGTERM SIGHUP

directories=()
while read -d $'\n'; do
        directories+=("$REPLY")
done < <(find docs/ -name 'index.rst' -printf '%h\n' | sort -u )

for dir in "${{directories[@]}}"; do
echo
echo "#############################"
echo "Building DOCS in ${{dir##*/}}"
echo "#############################"
echo

if [[ ! -d docs/output/"${{dir##*/}}/" ]]; then
  mkdir -p docs/output/"${{dir##*/}}/"
fi

sphinx-build -b html -E -c docs/etc/ ""$dir"/" docs/output/"${{dir##*/}}/"

done

