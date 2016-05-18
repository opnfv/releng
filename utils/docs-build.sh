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
VENV_DIR=${VENV_DIR:-$BUILD_DIR/_venv}
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
html_notes="    Revision: $rev_full\n    Build date: $(date -u +'%Y-%m-%d')"
opnfv_logo='releng/docs/etc/opnfv-logo.png'
copyright="$(date +%Y), OPNFV"

function check_rst_doc() {
    _src="$1"

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
            echo "      See http://artifacts.opnfv.org/releng/docs/how-to-use-docs ."
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

# Note: This script supports config override by creating 'config.py' file
#       in the document dir (e.g. docs/abc/config.py). If this file exists,
#       the original would be copied into the output dir as config to be
#       used during the build. If not, empty file would be created.
#       Then all other default parameters will be automatically added.
# Note: If you feel that your configuration or extensions would be useful
#       for other projects too, we encourage you to propose a change in the
#       releng repository. For further guidance see docs/how-to-use-docs/.
#       Also please edit this document once you change the default values.
function prepare_config() {
    _src="$1"
    _name="$2"
    _conf="$_src/conf.py"

    # default params
    # Note: If you want to add a new sphinx extention here, you may need python
    #       package for it (e.g. python package 'sphinxcontrib-httpdomain' is
    #       required by 'sphinxcontrib.httpdomain'). If you need such python
    #       package, add the name of the python package into the requirement
    #       list 'docs/etc/requirements.txt' .
    add_config "$_conf" 'extensions' \
    "['sphinxcontrib.httpdomain', 'sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.napoleon']"
    add_config "$_conf" 'needs_sphinx' "'1.3'"
    add_config "$_conf" 'numfig' "True"
    add_config "$_conf" 'master_doc' "'index'"
    add_config "$_conf" 'pygments_style' "'sphinx'"
    add_config "$_conf" 'html_use_index' "False"
    add_config "$_conf" 'html_logo' "'opnfv-logo.png'"
    add_config "$_conf" 'latex_domain_indices' "False"
    # Note: We have to make sure OPNFV logo is readable from the working space.
    add_config "$_conf" 'latex_logo' "'../../../$opnfv_logo'"

    # genarated params
    title=$(cd $_src; python -c "$get_title_script")
    latex_conf="[('index', '$_name.tex', \"$title\", 'OPNFV', 'manual'),]"
    add_config "$_conf" 'latex_documents' "$latex_conf"
    add_config "$_conf" 'release' "u'$version'"
    add_config "$_conf" 'version' "u'$version'"
    add_config "$_conf" 'project' "u'$project'"
    add_config "$_conf" 'copyright' "u'$copyright'"
    add_config "$_conf" 'rst_epilog' "u'$html_notes'"

    echo "sphinx config to be used:"
    echo
    sed -e "s/^/    /" "$_conf"
    echo
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
    echo "Error: $RELENG_DIR dir not found. See http://artifacts.opnfv.org/releng/docs/how-to-use-docs ."
    exit 1
fi

prepare_src_files

if ! which virtualenv > /dev/null ; then
    echo "Error: 'virtualenv' not found. Exec 'sudo pip install virtualenv' first."
    exit 1
fi

virtualenv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install -r "$RELENG_DIR/docs/etc/requirements.txt"

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

    echo
    echo "#################${dir//?/#}"
    echo "Building DOCS in $dir"
    echo "#################${dir//?/#}"
    echo

    prepare_config "$src" "$name"

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

deactivate
