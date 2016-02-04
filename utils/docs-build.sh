#!/bin/bash -e
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 NEC and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
export PATH=$PATH:/usr/local/bin/

DOCS_DIR=${DOCS_DIR:-docs}
INDEX_RST=${INDEX_RST:-index.rst}
BUILD_DIR=${BUILD_DIR:-docs_build}
OUTPUT_DIR=${OUTPUT_DIR:-docs_output}
SRC_DIR=${SRC_DIR:-$BUILD_DIR/_src}
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
html_notes="    Revision: $rev_full\n    Build date: |today|"
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
    _out=$(doc8 --max-line-length 240 --ignore D000 "$_src") || {
        _msg='Warning: rst validation (doc8) has failed, please fix the following error(s).'
        _errs=$(echo "$_out" | sed -n -e "/^$_src/s/^/    /p")
        echo
        echo -e "$_msg\n$_errs"
        echo
        [[ -n "$GERRIT_COMMENT" ]] && echo -e "$_msg\n$_errs" >> "$GERRIT_COMMENT"
    }
}

function add_html_notes() {
    _src="$1"

    find "$_src" -name '*.rst' | while read file
    do
        if grep -q -e ' _sha1_' "$file" ; then
            # TODO: remove this, once old templates were removed from all repos.
            echo
            echo "Warn: '_sha1_' was found in [$file], use the latest document template."
            echo "      See https://wiki.opnfv.org/documentation/tools ."
            echo
            sed -i "s/ _sha1_/ $git_sha1/g" "$file"
        fi
        sed -i -e "\$a\\\n..\n$html_notes" "$file"
    done
}

function prepare_src_files() {
    mkdir -p "$(dirname $SRC_DIR)"

    [[ -e "$SRC_DIR" ]] && rm -rf "$SRC_DIR"
    cp -r "$DOCS_DIR" "$SRC_DIR"
    add_html_notes "$SRC_DIR"
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

function is_top_dir() {
    [[ "$1" == "$DOCS_DIR" ]]
}

function generate_name_for_top_dir() {
    for suffix in '' '.top' '.all' '.master' '_' '__' '___'
    do
        _name="$(basename $DOCS_DIR)$suffix"
        [[ -e "$DOCS_DIR/$_name" ]] && continue
        echo "$_name"
        return
    done

    echo "Error: cannot find name for top directory [$DOCS_DIR]"
    exit 1
}

function generate_name() {
    _dir=$1

    if is_top_dir "$_dir" ; then
        _name=$(generate_name_for_top_dir $DOCS_DIR)
    else
        _name="${_dir#$DOCS_DIR/}"
    fi
    # Replace '/' by '_'
    echo "${_name////_}"
}


check_rst_doc $DOCS_DIR

if [[ ! -d "$RELENG_DIR" ]] ; then
    echo "Error: $RELENG_DIR dir not found. See https://wiki.opnfv.org/documentation/tools ."
    exit 1
fi

prepare_src_files

find $DOCS_DIR -name $INDEX_RST -printf '%h\n' | while read dir
do
    name=$(generate_name $dir)
    if is_top_dir "$dir" ; then
        src="$SRC_DIR"
    else
        src="$SRC_DIR/${dir#$DOCS_DIR/}"
    fi
    build="$BUILD_DIR/$name"
    output="$OUTPUT_DIR/$name"
    conf="$src/conf.py"

    echo
    echo "#################${dir//?/#}"
    echo "Building DOCS in $dir"
    echo "#################${dir//?/#}"
    echo

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

    # TODO: failures in ODT creation should be handled error and
    #       cause 'exit 1' before OPNFV B release.
    tex=$(find $build -name '*.tex' | head -1)
    odt="${tex%.tex}.odt"
    if [[ -e $tex ]] && which pandoc > /dev/null ; then
        (
            cd $(dirname $tex)
            pandoc $(basename $tex) -o $(basename $odt)
        ) && {
            mv $odt $output/
        }|| {
            msg="Error: ODT creation for $dir has failed."
            echo
            echo "$msg"
            echo
        }
    else
        echo "Warn: tex file and/or 'pandoc' are not found, skip ODT creation."
    fi

    if is_top_dir "$dir" ; then
        # NOTE: Having top level document (docs/index.rst) is not recommended.
        #       It may cause conflicts with other docs (mostly with HTML
        #       folders for contents in top level docs and other document
        #       folders). But, let's try merge of those contents into the top
        #       docs directory.
        (
            cd $output
            find . -type d -print | xargs -I d mkdir -p ../d
            find . -type f -print | xargs -I f mv -b f ../f
        )
        rm -rf "$output"
    fi

done
