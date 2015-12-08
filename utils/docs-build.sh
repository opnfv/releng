#!/bin/bash -e

export PATH=$PATH:/usr/local/bin/


SRC_DIR=${SRC_DIR:-docs}
INDEX_RST=${INDEX_RST:-index.rst}
BUILD_DIR=${BUILD_DIR:-build}
OUTPUT_DIR=${OUTPUT_DIR:-output}
RELENG_DIR=${RELENG_DIR:-releng}
GERRIT_COMMENT=${GERRIT_COMMENT:-}

get_title_script="
import os
from docutils import core, nodes

try:
    with open('index.rst', 'r') as file:
        data = file.read()
    doctree = core.publish_doctree(data,
        settings_overrides={'report_level': 5,
                            'halt_level': 5})
    if isinstance(doctree[0], nodes.title):
        title = doctree[0]
    else:
        for c in doctree.children:
            if isinstance(c, nodes.section):
                title = c[0]
                break
    print title.astext()
except:
    print 'None'"
revision="$(git rev-parse --short HEAD)"
rev_full="$(git rev-parse HEAD)"
version="$(git describe --abbrev=0 2> /dev/null || echo draft) ($revision)"
project="$(basename $(git rev-parse --show-toplevel))"
html_notes="\n    Revision: $rev_full\n\n    Build date: |today|"
default_conf='releng/docs/etc/conf.py'
opnfv_logo='releng/docs/etc/opnfv-logo.png'

function check_rst_doc() {
    _src="$1"

    if ! which doc8 > /dev/null ; then
        echo "Error: 'doc8' not found. Exec 'sudo pip install doc8' first."
        exit 1
    fi
    # Note: This check may fail in many jobs for building project docs, since
    #       the old sample has lines more than 120. We ignore failures on this
    #       check right now, but these have to be fixed before OPNFV B release.
    _out=$(doc8 --max-line-length 120 "$_src") || {
        _msg='Error: rst validatino (doc8) has failed, please fix the following error(s).'
        _errs=$(echo "$_out" | sed -n -e "/^$_src/s/^/    /p")
        echo
        echo -e "$_msg\n$_errs"
        echo
        [[ -n "$GERRIT_COMMENT" ]] && echo -e "$_msg\n$_errs" >> "$GERRIT_COMMENT"
    }
}

function add_html_notes() {
    _src="$1"
    _dir="$2"

    if grep -q -e ' _sha1_' "$_src"/*.rst ; then
        # TODO: remove this, once old templates were removed from all repos.
        echo
        echo "Warn: '_sha1_' was found in $_dir , use the latest document template."
        echo "      See https://wiki.opnfv.org/documentation/tools ."
        echo
        sed -i "s/ _sha1_/ $git_sha1/g" "$_src"/*.rst
    fi
    sed -i -e "\$a\\\n.. only:: html\n$html_notes" "$_src"/*.rst
}

function add_config() {
    _conf="$1"
    _param="$2"
    _val="$3"

    if ! grep -q -e "^$_param = " "$_conf" ; then
        echo "Adding '$_param' into $_conf ..."
        echo "$_param = $_val" >> "$_conf"
    fi
}


check_rst_doc $SRC_DIR

if [[ ! -d "$RELENG_DIR" ]] ; then
    echo "Error: $RELENG_DIR dir not found. See https://wiki.opnfv.org/documentation/tools ."
    exit 1
fi

find $SRC_DIR -name $INDEX_RST -printf '%h\n' | while read dir
do
    name="${dir##*/}"
    src="$BUILD_DIR/src/$name"
    build="$BUILD_DIR/$name"
    output="$OUTPUT_DIR/$name"
    conf="$src/conf.py"

    echo
    echo "#################${dir//?/#}"
    echo "Building DOCS in $dir"
    echo "#################${dir//?/#}"
    echo

    mkdir -p "$BUILD_DIR/src"
    [[ -e "$src" ]] && rm -rf "$src"
    cp -r "$dir" "$src"

    add_html_notes "$src" "$dir"

    [[ ! -f "$conf" ]] && cp "$default_conf" "$conf"
    title=$(cd $src; python -c "$get_title_script")
    latex_conf="[('index', '$name.tex', \"$title\", 'OPNFV', 'manual'),]"
    add_config "$conf" 'latex_documents' "$latex_conf"
    add_config "$conf" 'release' "u'$version'"
    add_config "$conf" 'version' "u'$version'"
    add_config "$conf" 'project' "u'$project'"
    add_config "$conf" 'copyright' "u'$(date +%Y), OPNFV'"
    cp -f $opnfv_logo "$src/opnfv-logo.png"

    mkdir -p "$output"

    sphinx-build -b html -t html -E "$src" "$output"

    # Note: PDF creation may fail in project doc builds.
    #       We allow this build job to be marked as succeeded with
    #       failure in PDF creation, but leave message to fix it.
    #       Any failure has to be fixed before OPNFV B release.
    {
        sphinx-build -b latex -t pdf -E "$src" "$build" && \
            make -C "$build" LATEXOPTS='--interaction=nonstopmode' all-pdf
    } && {
        mv "$build/$name.pdf" "$output"
    } || {
        msg="Error: PDF creation for $dir has failed, please fix source rst file(s)."
        echo
        echo "$msg"
        echo
        [[ -n "$GERRIT_COMMENT" ]] && echo "$msg" >> "$GERRIT_COMMENT"
    }

done
