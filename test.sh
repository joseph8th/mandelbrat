#!/usr/bin/env bash

TEST=test_fun
TEST2=test_fun2

function test_fun {
    echo "Yep."
}

function test_fun2 {
    [ -e test.txt ] && rm test.txt
    touch test.txt
    str="\
Yep.\n\
Yep.\n\
Yep.\n"
    printf $str >> test.txt
}

[ ! -z $TEST ] && $TEST

if [ ! -z $TEST2 ]; then
    $TEST2
fi

if [ ! -z $TEST3 ]; then
    $TEST3
fi

