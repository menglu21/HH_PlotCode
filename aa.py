from ROOT import TFile

Ntot=0
Njet3=0
Njet4=0

path='TT_ele_CR_2J/TTto2L/TTto2L_'
for i in range(0,99):
  filein_=path+str(i)+'/output.root'
  print('file:',filein_)
  filein=TFile.Open(filein_)
  nweight=filein.Get('nEventsGenWeighted')
  if not nweight:continue
  print('Nweight:',nweight.GetBinContent(1))
  Ntot=Ntot+nweight.GetBinContent(1)
  njet=filein.Get('nTightAK4JetCRall_ele_CR_noSF')
  print(njet.GetBinContent(3),njet.GetBinContent(4))
  Njet3=Njet3+njet.GetBinContent(3)
  Njet4=Njet4+njet.GetBinContent(4)

print(Ntot, Njet3, Njet4)
