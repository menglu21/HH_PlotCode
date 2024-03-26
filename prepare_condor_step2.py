import os,json
import sys
from os import walk

def prepare_condor():
  for root, dirs, files in os.walk(BASIC_PATH,topdown = False):
        samples=files
  return samples


BASIC_PATH="/eos/user/m/melu/HH_2017merged/"
PWD=os.getcwd()

samplejson='samples2017.json'

samples_name=[]
samples_dir=[]

with open(samplejson, 'r') as fin:
  data=fin.read()
  lines=json.loads(data)
  keys=lines.keys()
  for key, value in lines.items():
    samples_dir.append(key)
    samples_name.append(value[0])

#region: onelep_b_region, onelep_nob_region, tt2L_region, dy_region
Region = sys.argv[1]
#category: one, two (one lep or two lep category)
Channel = sys.argv[2]
Category = sys.argv[3]

if __name__ == "__main__":

  WORKING_DIR=Region+'_'+Channel+'_'+Category
  os.mkdir(WORKING_DIR)

  samples_counts=[]
  samples_ineos=prepare_condor()
  wrapper_dir=PWD+'/wrapper.sh'

  sample_dict={}
  for iname in range(0,len(samples_name)):
    sample_dict[samples_name[iname]]=[]

#  print('samples_name:',samples_name)
#  print('samples_ineos:',samples_ineos)

  for iname in range(0,len(samples_name)):
    for isamp in samples_ineos:
      if isamp.startswith('QCD_Pt'):continue
      if (isamp.startswith(samples_name[iname]+'.') or isamp.startswith(samples_name[iname]+'_')) and (isamp not in sample_dict[samples_name[iname]]) :sample_dict[samples_name[iname]].append(isamp)

  for iname in range(0,len(samples_name)):
    samples_counts.append(len(sample_dict[samples_name[iname]]))

  for iname in range(0,len(samples_dir)):
    if 'signal' in samples_dir[iname]:continue
    print(samples_dir[iname])
    print(PWD)
    os.mkdir(samples_dir[iname])
    os.chdir(samples_dir[iname])

    if 'TT' in samples_dir[iname]:
      beff_name='../b_eff/TTto2L_beff.root'
    elif 'ttWtoLNu' == samples_dir[iname]:
      beff_name='../b_eff/ttWtoLNu_beff.root'
    elif 'ttWtoQQ' == samples_dir[iname]:
      beff_name='../b_eff/ttWtoQQ_beff.root'
    elif 'tW' == samples_dir[iname]:
      beff_name='../b_eff/tW_beff.root'
    elif 'tbarW' in samples_dir[iname]:
      beff_name='../b_eff/tbarW_beff.root'
    elif 'ttWW' == samples_dir[iname]:
      beff_name='../b_eff/ttWW_beff.root'
    elif 'ttWZ' == samples_dir[iname]:
      beff_name='../b_eff/ttWZ_beff.root'
    elif 'ttZ' == samples_dir[iname]:
      beff_name='../b_eff/ttZ_beff.root'
    elif 'ttZtoQQ' == samples_dir[iname]:
      beff_name='../b_eff/ttZtoQQ_beff.root'
    elif 'tZq' in samples_dir[iname]:
      beff_name='../b_eff/tZq_beff.root'
    elif 'dy' in samples_dir[iname]:
      beff_name='../b_eff/DY_beff.root'
    elif 'ww_' in samples_dir[iname]:
      beff_name='../b_eff/DY_beff.root'
#    elif os.path.exists('../b_eff/'+samples_dir[iname]+'_bEff.root'):
#      beff_name='../b_eff/'+samples_dir[iname]+'_bEff.root'
    else:
      beff_name='../b_eff/TTto2L_beff.root'
    os.system(r'cp ../make_hists.py .')
    os.system(r'cp %s ./bEff.root'%(beff_name) )
    os.system(r'cp ../HH.h .')
    os.system(r'cp ../eleIDSF.root .')
    os.system(r'cp ../muIDSF.root .')
    os.system(r'cp ../fr_mu.root .')
    os.system(r'cp ../TriggerSF_ele.root .')
    os.system(r'cp ../TriggerSF_mu.root .')
    os.system(r'cp ../sub.jdl .')
    for i in range(0,samples_counts[iname]):
      os.mkdir(samples_dir[iname]+'_'+str(i))
      os.chdir(samples_dir[iname]+'_'+str(i))
      os.system(r'cp %s .'%(wrapper_dir))
      name_temp=BASIC_PATH+sample_dict[samples_name[iname]][i]
      name_temp=name_temp.replace("/","DUMMY")
      os.system(r'sed -i "s/dummyroot/%s/g" wrapper.sh' %(name_temp))
      os.system(r'sed -i "s/INPUT/%s/g" wrapper.sh' %(name_temp.split('DUMMY')[-1]))
      os.system(r'sed -i "s/REGION/%s/g" wrapper.sh' %(Region))
      os.system(r'sed -i "s/CHANNEL/%s/g" wrapper.sh' %(Channel))
      os.system(r'sed -i "s/CATEGORY/%s/g" wrapper.sh' %(Category))
      os.system(r'sed -i "s/PROCESS/%s/g" wrapper.sh' %(samples_dir[iname]))
      os.system(r'sed -i "s/DUMMY/\//g" wrapper.sh')
      if 'Fake' in samples_dir[iname]:
        os.system(r'sed -i "s/prompt/Fake/g" wrapper.sh')
      os.chdir(PWD+'/'+samples_dir[iname])
    os.chdir(PWD+'/'+samples_dir[iname])
    os.system(r'sed -i "s/NUMBER/%s/g" sub.jdl' %(samples_counts[iname]))
    os.system(r'sed -i "s/DUMMY/%s/g" sub.jdl' %(samples_dir[iname]))
    os.chdir(PWD)
    os.system(r'mv %s %s'%(samples_dir[iname], WORKING_DIR))

