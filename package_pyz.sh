#!/bin/bash

CURR_DIR=$(pwd)
TEMP_DIR=$(mktemp -d)
function cleanup {
    rm -rf $TEMP_DIR
}
trap cleanup EXIT

function install_ply {
    cd $TEMP_DIR
    wget -qO - https://github.com/dabeaz/ply/archive/master.tar.gz | tar xzf -

    cd ply-master
    cp -r ply $1
}

function install_pyxtuml {
    cd $TEMP_DIR
    wget -qO - https://github.com/john-tornblom/pyxtuml/archive/master.tar.gz | tar xzf -

    cd pyxtuml-master
    PYTHONPATH=$1 python setup.py build
    cp -r xtuml $1
    cp -r bridgepoint $1
}

function install_pyrsl {
    cd $TEMP_DIR
    wget -qO - https://github.com/john-tornblom/pyrsl/archive/master.tar.gz | tar xzf -

    cd pyrsl-master
    PYTHONPATH=$1 python setup.py build
    cp -r rsl $1
}

function install_main {
    echo "from rsl import gen_erate" >  $1/__main__.py
    echo "gen_erate.main()"          >> $1/__main__.py
}


function make_executable {
    python -m zipfile -c $TEMP_DIR/pkg.zip $1/*
    echo "#!/usr/bin/env python" > $2
    cat $TEMP_DIR/pkg.zip >> $2
    chmod +x $2
}


mkdir $TEMP_DIR/inst || exit 1

echo ""
echo "Fetching from github and packaging, please wait..."
echo ""

install_main    $TEMP_DIR/inst || exit 1
install_ply     $TEMP_DIR/inst || exit 1
install_pyxtuml $TEMP_DIR/inst || exit 1
install_pyrsl   $TEMP_DIR/inst || exit 1

make_executable $TEMP_DIR/inst $CURR_DIR/gen_erate.pyz || exit 1

echo ""
echo "Executable successfully created"
echo ""
echo "    $CURR_DIR/gen_erate.pyz"
