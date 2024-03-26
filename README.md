# HH_PlotCode
### the directory b_eff contains the btag efficiencies for all the MC processes, two working points are included (Loose and Medium), three flavors are included (light, c-quark, b-quark)
* step 0: login to lxplus8, create a directory for the plot code under your WORK/DIRECTORY, HH_Plot
* step 1:
  ```
  cmsrel CMSSW_12_4_18
  cd CMSSW_12_4_18/src
  cmsenv
  cd -
  cd HH_Plot
  git clone https://github.com/menglu21/HH_PlotCode/tree/datadriven_lxplus8
  ```
* step 2: use file prepare_condor_step2.py to prepare the condor code to produce the histograms, file make_hists.py is used to get the histograms, in which the seclections are define. If you want to produce histograms for TTbar CR region in di-muon channel, you can use following command
  ```
  python3 prepare_condor_step2.py TT muon CR
  ```
  if you want to produce histograms in SR0F signal region in di-muon channel, you can use following command
  ```
  python3 prepare_condor_step2.py SR0F muon SR
  ```
  after the above command, you should get a directory named TT_muon_CR or SR0F_muon_SR, depends on your previous command, you will find there will be many sub-directories which correspond to each process (both MC and data)
* step 3: then use file submit_step3.py to submit the condor jobs, e.g.
  ```
  python3 submit_step3.py 1 TT_muon_CR
  ```
  if you check the parameters in submit_step3.py, you will find "1" here indicate submit the muon channel
* step 4: you can always use ```condor_q``` to monitor the status of your jobs, if all the jobs finish, you can use following command to merge all the jobs for each process
  ```
  python3 mergeOutput_step4.py 1 TT_muon_CR
  ```
  One thing needs to be kept in mind is that, ALL THE DATA JOBS should be finished, otherwise you will lost data event. For MC jobs, it's fine that some of them are not complete or will some error during condor jobs, but you should remove them before you execetu the ```mergeOutput_step4.py```. You can use script ```checkjobs``` to check the job size, e.g.
  ```
  cd TT_muon_CR
  ../checkjobs DY
  ```
  if the size of some files are 1.0K or 4.0K, you can remove those files.
* step 5, go to directory Plot, get ready for the plots. 
  ```
  cd Plot
  python3 plot.py ../TT_muon_CR/ Btag 2017 1
  ```
