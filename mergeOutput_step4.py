import os,json
import sys
from os import walk

submit_data=int(sys.argv[1])
Working_path=sys.argv[2]
print(submit_data)

os.chdir(Working_path)
BASIC_PATH=os.getcwd()
FINAL=BASIC_PATH.split('/')[-1]
for root, dirs, files in os.walk(BASIC_PATH,topdown = False):
  if not FINAL==root.split('/')[-1]:continue
  samples_dir=dirs

for isamp in samples_dir:
  if 'Single' in isamp:
    if submit_data==1 and 'SingleMuon' in isamp:
      print('merge muon data output:', isamp)
      os.chdir(isamp)
      os.system(r"hadd %s.root %s_*/output.root"%(isamp,isamp))
      os.system(r"hadd %s_slim.root %s_*/slim.root"%(isamp,isamp))
      os.system(r"mv %s.root ../"%(isamp))
      os.system(r"mv %s_slim.root ../"%(isamp))
      os.chdir(BASIC_PATH)
    if submit_data==2 and 'SingleEle' in isamp:
      print('merge ele data output:', isamp)
      os.chdir(isamp)
      print('HERE!!',os.getcwd())
      os.system(r"hadd %s.root %s_*/output.root"%(isamp,isamp))
      os.system(r"hadd %s_slim.root %s_*/slim.root"%(isamp,isamp))
      os.system(r"mv %s.root ../"%(isamp))
      os.system(r"mv %s_slim.root ../"%(isamp))
      os.chdir(BASIC_PATH)
  else:
    print('merge MC output:',isamp)
    os.chdir(isamp)
    os.system(r"hadd %s.root %s_*/output.root"%(isamp,isamp))
    os.system(r"hadd %s_slim.root %s_*/slim.root"%(isamp,isamp))
    os.system(r"mv %s.root ../"%(isamp))
    os.system(r"mv %s_slim.root ../"%(isamp))
    os.chdir(BASIC_PATH)

#os.mkdir('HIST_output')
#os.chdir('HIST_output')
#os.system('mv ../*.root .')
#os.chdir(BASIC_PATH)
