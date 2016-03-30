#!/bin/bash

CURR_DIR=$(pwd)
TEMP_DIR=$(mktemp -d)
function cleanup {
    rm -rf $TEMP_DIR
}
trap cleanup EXIT

function install_ply {
    cd $TEMP_DIR
    wget -qO - https://github.com/dabeaz/ply/archive/$1.tar.gz | tar xzf -

    cd ply-*
    cp -r ply $2
}

function install_pyxtuml {
    cd $TEMP_DIR
    wget -qO - https://github.com/xtuml/pyxtuml/archive/$1.tar.gz | tar xzf -

    cd pyxtuml-*
    ln -s $2/ply ply
    PYTHONPATH=$2 python setup.py build
    cp -r xtuml $2
    cp -r bridgepoint $2
}

function install_pyrsl {
    cd $TEMP_DIR
    wget -qO - https://github.com/xtuml/pyrsl/archive/$1.tar.gz | tar xzf -

    cd pyrsl-*
    ln -s $2/ply ply
    ln -s $2/xtuml xtuml
    PYTHONPATH=$2 python setup.py build
    cp -r rsl $2
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

PLY=master
PYXTUML=master
PYRSL=master
MAIN=""

for i in "$@"
do
    case $i in
	-ply)
	    PLY=$2
	    shift 1
	    ;;
	-pyxtuml)
	    PYXTUML=$2
	    shift 1
	    ;;
	-pyrsl)
	    PYRSL=$2
	    shift 1
	    ;;
	-main)
	    MAIN=$2
	    shift 1
	    ;;
	-h|-help|--help)
	    echo "Usage:"
	    echo "  $0 [options]"
	    echo ""
	    echo "Options:"
	    echo "  -ply <git tag or branch>      Bundle with a specific version of ply hosted on github.com/dabeaz/ply"
	    echo "  -pyxtuml <git tag or branch>  Bundle with a specific version of pyxtuml hosted on github.com/xtuml/pyxtuml"
	    echo "  -pyrsl <git tag or branch>    Bundle with a specific version of pyrsl hosted on github.com/xtuml/pyrsl"
	    echo "  -main <path>                  Provide a custom python entry point (__main__.py)."
	    echo ""
	    echo "Description:"
	    echo "  Create a self-contained python zip app from pyrsl."
	    exit 0
	    ;;
	-*)
            echo "unknown option $i"
	    exit -1
	    ;;
	*)
	    shift 1
	    ;;
    esac
done

mkdir $TEMP_DIR/inst || exit 1

if [ -z "$MAIN" ]; then
    install_main  $TEMP_DIR/inst || exit 1
else
    echo "Using $MAIN as entry point"
    cp $MAIN $TEMP_DIR/inst/__main__.py
fi


echo ""
echo "Fetching from github and packaging, please wait..."
echo ""

install_ply     $PLY     $TEMP_DIR/inst || exit 1
install_pyxtuml $PYXTUML $TEMP_DIR/inst || exit 1
install_pyrsl   $PYRSL   $TEMP_DIR/inst || exit 1

make_executable $TEMP_DIR/inst $CURR_DIR/gen_erate.pyz || exit 1

echo ""
echo "Executable successfully created: $CURR_DIR/gen_erate.pyz"
echo "Configurations:"
echo "  ply      $PLY"
echo "  pyxtuml  $PYXTUML"
echo "  pyrsl    $PYRSL"

