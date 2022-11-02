#!/bin/bash

# este script genera las imágenes de los autómatas
# a partir de los .dot generados por
# our_test_to_deterministic.py y our_test_to_minimized.py  

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

DOT_FILES_DIR="${SCRIPT_DIR}/dot"
IMGS_DIR="${SCRIPT_DIR}/img"

mkdir -p $IMGS_DIR

for file in $( ls $DOT_FILES_DIR)
do
    dot -Tpng ${DOT_FILES_DIR}/${file} > "${IMGS_DIR}/${file%.*}.png"
done