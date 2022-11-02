#!/bin/bash


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

DOT_FILES_DIR="${SCRIPT_DIR}/dot"
IMGS_DIR="${SCRIPT_DIR}/img"

mkdir -p $IMGS_DIR

for file in $( ls $DOT_FILES_DIR)
do
    dot -Tpng ${DOT_FILES_DIR}/${file} > "${IMGS_DIR}/${file%.*}.png"
done