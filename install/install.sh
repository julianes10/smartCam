#!/bin/bash 
echo "Here we go: $@"
echo "------------------------------------------------------------------"
echo "- This script must me executed from root project                 -"  
echo "- Review install/pivars.sh for specific settings for this projet -"
echo "------------------------------------------------------------------"
cmd="./SCS/utils/deploySoftware.sh ./install/pivars.sh $@"
echo "Executing $cmd"
$cmd
aux=$?
exit $aux




