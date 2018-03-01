#!/bin/bash
for f in in/*.in; do
    name=$(echo $f | sed "s/in//g" | sed "s/[\.\/]//g")
    echo $name
    python2 main.py $name
done

