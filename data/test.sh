#!/bin/bash
function bash_cmd(){
echo $1 
check=eval $1
if [ $? -gt 0 ]; then
    echo "successful -> $1 $?"
    return $?
else
    echo "unsuccessful"
    exit $2
fi
}
clear
echo "ls -als | wc -l"
bash_cmd $(ls -als | wc -l) 1
#echo $?
#var2=$(df -h | wc -l)

#var2=$(df -h)
#eval $var2
#bash_cmd $var2 1
#bash_cmd $var2 1
echo $?