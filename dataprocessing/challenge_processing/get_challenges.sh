#!/bin/bash
# vim: set expandtab tabstop=4 shiftwidth=4:

for dir in basegame/*
do
    echo $dir
    cd $dir
    ../../process_challenges.py >> ../../challenges.py
    cd ../..
done

for dir in dlc1/*
do
    echo $dir
    cd $dir
    ../../process_challenges.py >> ../../challenges-dlc1.py
    cd ../..
done

for dir in dlc2/*
do
    echo $dir
    cd $dir
    ../../process_challenges.py >> ../../challenges-dlc2.py
    cd ../..
done
