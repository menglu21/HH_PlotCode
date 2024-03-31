#!/bin/bash -e 
echo "TEST FIRST" 
#echo "copy input root file"
#eoscp dummyroot ./INPUT
PWD=`pwd`
HOME=$PWD
echo $HOME 
export SCRAM_ARCH=el8_amd64_gcc10
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval "scramv1 project CMSSW CMSSW_12_4_18"
cd $PWD/CMSSW_12_4_18
ls -lrth
eval `scramv1 runtime -sh`

cd #PWD
echo "TEST DIR"

#python make_hists.py -i INPUT -r REGION -c CHANNEL -t CATEGORY
python3 make_hists.py -i dummyroot -r REGION -c CHANNEL -t CATEGORY
printf "end!!!"
ls -lrth
rm -rf CMSSW_12_4_18
ls *.root | grep -v -E "slim\.root|output\.root" |xargs rm
ls -lrth
