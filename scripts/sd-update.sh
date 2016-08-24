#!/bin/bash
set -e

clear_files="server/Procfile server/app.py"
use_branch='master'
force=''
quick=false
mydir=$(readlink -e $(dirname "$0"))

script_name=`basename $0`

function show_help {
    echo "$script_name [-h] [-f] [-b 'branch']"
    echo -e "\t-h - show help"
    echo -e "\t-f - force push to origin"
    echo -e "\t-q - quick; skip updating requirements"
    echo -e "\t-b 'branch' - pull from branch"
}

TEMP=`getopt -o hfqb: --long force,quick,branch: -n '$script_name' -- "$@"`
eval set -- "$TEMP"

while true; do
    case "$1" in
    -h) show_help; exit 0 ;;
    -f|--force) force='--force'; shift ;;
    -q|--quick) quick=true; shift ;;
    -b|--branch) use_branch=$2; shift ;;
    *) shift; break ;;
    esac
done

flag_count=`git status --porcelain | sed -e 's/^[ \t]*//' | cut -f 1 -d ' ' | sed 's/[^MAD]//g' | wc -w`
if [ $flag_count -gt 0 ]; then modified=true; else modified=false; fi

function cleanup {
    $modified && git stash pop
}

trap cleanup EXIT

$modified && git stash

if ! git pull -r sd $use_branch; then
    [ $modified ] && git stash pop
    exit 1
fi

git push $force origin $use_branch

if ! $quick; then
    cd client && npm update
    cd ..

    cd server && pip install -r requirements.txt -U
    cd ..
fi

$modified && git stash pop
