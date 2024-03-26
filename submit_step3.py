import os,json
import sys
from os import walk

submit_data=int(sys.argv[1])
Working_path=sys.argv[2]

if submit_data==0:
  print('dont submit data')
if submit_data==1:
  print('will submit muon')
if submit_data==2:
  print('will submit ele')


os.chdir(Working_path)
BASIC_PATH=os.getcwd()
FINAL=BASIC_PATH.split('/')[-1]
for root, dirs, files in os.walk(BASIC_PATH,topdown = False):
  if not FINAL==root.split('/')[-1]:continue
  samples_dir=dirs
  print(samples_dir)

for isamp in samples_dir:
  if 'Single' in isamp:
    if submit_data==1 and 'SingleMuon' in isamp:
      print('submit muon data samples:', isamp)
      os.chdir(isamp)
      os.system(r'condor_submit sub.jdl')
      os.chdir(BASIC_PATH)
    if submit_data==2 and 'SingleElectron' in isamp:
      print('submit ele data samples:', isamp)
      os.chdir(isamp)
      os.system(r'condor_submit sub.jdl')
      os.chdir(BASIC_PATH)
  else:
    print('submit MC samples:',isamp)
    os.chdir(isamp)
    os.system(r'condor_submit sub.jdl')
    os.chdir(BASIC_PATH)
