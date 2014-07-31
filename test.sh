#!/usr/bin/env bash

TEST=
TEST2=
TEST3=test_fun3


function test_fun {
    string="poopy"
    substr1="duh"
    substr2="py"
    if [[ $(expr index "$string" "$substr1") -ne "0" ]]; then
        echo "$substr1"
    fi
    if [[ $(expr index "$string" "$substr2") -ne "0" ]]; then
        echo "$substr2"
    fi
    
    dir1=./*
    dir2=~/.pyenv/versions/*
    for d in $dir1; do
        if [[ "$d" == *"_arc" ]]; then
            echo $d
        fi
    done

}

function test_fun2 {
    [ -e test.txt ] && rm test.txt
    touch test.txt

    v1="poo"
    v2="who"
    str="\
v1='${v1}'\n\
v2=\'${v2}\'\n\
Yep.\n"
    printf $str >> test.txt
}

function test_fun3 {
    TMPDIR=./tmp
    source ./pacbrat.d/gmp.sh
    run_install_gmp
}

[ ! -z $TEST ] && $TEST

if [ ! -z $TEST2 ]; then
    $TEST2
fi

if [ ! -z $TEST3 ]; then
    $TEST3
fi

