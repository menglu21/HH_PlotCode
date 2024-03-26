import ROOT,sys,os
import numpy as np
from ROOT import kFALSE
import time

import CMSTDRStyle
CMSTDRStyle.setTDRStyle().cd()
import CMSstyle
from array import array

def set_axis(the_histo, coordinate, title, is_energy):

  if coordinate == 'x':
    axis = the_histo.GetXaxis()
  elif coordinate == 'y':
    axis = the_histo.GetYaxis()
  else:
    raise ValueError('x and y axis only')
  
  axis.SetLabelFont(42)
  axis.SetLabelOffset(0.015)
  axis.SetNdivisions(505)
  axis.SetTitleFont(42)
  axis.SetTitleOffset(1.15)
  axis.SetLabelSize(0.03)
  axis.SetTitleSize(0.04)
  if coordinate == 'x':
    axis.SetLabelSize(0.0)
    axis.SetTitleSize(0.0)
  if (coordinate == "y"):axis.SetTitleOffset(1.2)
  if is_energy:
    axis.SetTitle(title+' [GeV]')
  else:
    axis.SetTitle(title) 

xs={
'QCD':239000,
'dy':6077.22,
't_tch':136.02,
'tbar_tch':80.95,
'tW':35.85,
'tbarW':35.85,
't_sch':3.36,
'TTto1L':365.4574,
'TTto2L':88.3419,
'ttW':0.1792,
'ttWToQQ':0.3708,
'ttWW':0.007003,
'ttWZ':0.002453,
'ttZ':0.2589,
'ttZToQQ':0.6012,
'ttZZ':0.001386,
'tzq':0.07561,
'wjet':61526.7,
'ww':11.09,
'ww_qq':50.85,
'www':0.2086,
'wwz':0.1707,
'wz_qcd':5.213,
'wz_qq':9.146,
'wzz':0.05709,
'zz2l':0.9738,
'zzz':0.01476
}

colors={
'SingleMuon':0,
'SingleEG':0,
'dy':2,
't_tch':3,
'tbar_tch':3,
'tW':3,
'tbarW':3,
't_sch':3,
'TTto1L':4,
'TTto2L':5,
'ttW':6,
'ttWToQQ':6,
'ttZ':6,
'ttZToQQ':6,
'ttWW':7,
'ttWZ':7,
'ttZZ':7,
'tzq':8,
'wjet':9,
'ww':11,
'ww_qq':11,
'wz_qcd':11,
'wz_qq':11,
'zz2l':11,
'QCD':30,
'www':41,
'wwz':41,
'wzz':41,
'zzz':41
}

DIRS = sys.argv[1]
VARYS = sys.argv[2]

def plot():
  BASIC_PATH=os.getcwd()
  BASIC_PATH=BASIC_PATH+'/'+DIRS
  for root, dirs, files in os.walk(BASIC_PATH,topdown = False):
    samples_list=files
  
#  fin=ROOT.TFile.Open(BASIC_PATH+'dy.root')
  fin=ROOT.TFile.Open(BASIC_PATH+samples_list[0])
  tlist=fin.GetListOfKeys()
  it = ROOT.TIter(tlist)
  elem = it.Next()
  
  histname_arr=[]
  
  # the first histogram is used for scaling, no plot
  while elem:
    name_tmp=elem.GetName()
    if VARYS=='noSF' and name_tmp.split('_')[-1]=='noSF':
      histname_arr.append(name_tmp)
    if VARYS=='ID' and name_tmp.split('_')[-1]=='ID':
      histname_arr.append(name_tmp)
    if VARYS=='ALL' and name_tmp.split('_')[-1]=='CR':
      histname_arr.append(name_tmp)
    if VARYS=='Btag' and name_tmp.split('_')[-1]=='Btag':
      histname_arr.append(name_tmp)
    elem = it.Next()

  fin.Close()

  lumi=41480.
  
  for ihist in range(1,len(histname_arr)):
#    if ihist>1:continue
    histos=[]
    histos_name=[]
    isenergy=False 
    if 'mll' in histname_arr[ihist] or 'mjj' in histname_arr[ihist] or 'HT' in histname_arr[ihist] or 'mass' in histname_arr[ihist] or 'pt' in histname_arr[ihist] or ('met' in histname_arr[ihist] and 'phi' not in histname_arr[ihist]):
      isenergy=True
  
    for iprocess in range(0,len(samples_list)):
      print(samples_list[iprocess])
      name_tmp=samples_list[iprocess].split('.')[0]
      fin_temp=ROOT.TFile.Open(BASIC_PATH+samples_list[iprocess])
      hist_temp_=fin_temp.Get(histname_arr[ihist])
      if 'signal' in name_tmp:continue
      if not ('Single' in name_tmp or name_tmp in xs.keys()):continue
      if not 'Single' in name_tmp:
        hist_normalize=fin_temp.Get('nEventsGenWeighted')
        hist_temp_.Scale(float(xs[name_tmp])*lumi/(hist_normalize.GetBinContent(1)))

      hist_temp=hist_temp_.Clone()
      #SetDirectory(0) is necessary to keep the histo alive when the root file is closed
      hist_temp.SetDirectory(0)
      histos.append(hist_temp)
      histos_name.append(name_tmp)
      fin_temp.Close()
  
    draw_plots(histos,histos_name,1,histname_arr[ihist],isenergy)


def draw_plots(hist_array =[], hist_name =[], draw_data=0, x_name='', isenergy=False):

  DY = hist_array[0].Clone()
  DY.Reset()
  DY.SetFillColor(2)
  signal=DY.Clone()
  signal.SetFillColor(46)
  WJet=DY.Clone()
  WJet.SetFillColor(9)
  SingleTop=DY.Clone()
  SingleTop.SetFillColor(3)
  TTto1L=DY.Clone()
  TTto1L.SetFillColor(4)
  TTto2L=DY.Clone()
  TTto2L.SetFillColor(5)
  TTV=DY.Clone()
  TTV.SetFillColor(6)
  TTVV=DY.Clone()
  TTVV.SetFillColor(7)
  TZq=DY.Clone()
  TZq.SetFillColor(8)
  VV=DY.Clone()
  VV.SetFillColor(11)
  VVV=DY.Clone()
  VVV.SetFillColor(41)
  QCD=DY.Clone()
  QCD.SetFillColor(30)

  Data=DY.Clone()

  for ihist in range(0,len(hist_name)):
    if 'Single' in hist_name[ihist]:
      Data.Add(hist_array[ihist])
    else:
      if colors[hist_name[ihist]]==2:
        DY.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==46:
        signal.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==3:
        SingleTop.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==4:
        TTto1L.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==5:
        TTto2L.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==6:
        TTV.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==7:
        TTVV.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==8:
        TZq.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==9:
        WJet.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==11:
        VV.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==41:
        VVV.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==30:
        QCD.Add(hist_array[ihist])

  Data.SetMarkerStyle(20)
  Data.SetMarkerSize(0.85)
  Data.SetMarkerColor(1)
  Data.SetLineWidth(1)


  h_stack = ROOT.THStack()
  h_stack.Add(DY)
  h_stack.Add(WJet)
  h_stack.Add(SingleTop)
  h_stack.Add(TTto1L)
  h_stack.Add(TTto2L)
  h_stack.Add(TTV)
  h_stack.Add(TTVV)
  h_stack.Add(VV)
  h_stack.Add(VVV)
  h_stack.Add(TZq)
  h_stack.Add(QCD)
  h_stack.Add(signal)
  max_yields = 0
  Nbins=h_stack.GetStack().Last().GetNbinsX()
  for i in range(1,Nbins+1):
    max_yields_temp = h_stack.GetStack().Last().GetBinContent(i)
    if max_yields_temp>max_yields:max_yields=max_yields_temp
  
  max_yields_data = 0
  for i in range(1,Nbins+1):
    max_yields_data_temp = Data.GetBinContent(i)
    if max_yields_data_temp>max_yields_data:max_yields_data=max_yields_data_temp
  
  h_stack.SetMaximum(max(max_yields, max_yields_data)*1.8)

  ##MC error
  h_error = h_stack.GetStack().Last()
  h_error.SetBinErrorOption(ROOT.TH1.kPoisson);
  binsize = h_error.GetSize()-2;
  x = [];
  y = [];
  xerror_l = [];
  xerror_r = [];
  yerror_u = [];
  yerror_d = [];
  for i in range(0,binsize):
    x.append(h_error.GetBinCenter(i+1))
    y.append(h_error.GetBinContent(i+1))
    xerror_l.append(0.5*h_error.GetBinWidth(i+1))
    xerror_r.append(0.5*h_error.GetBinWidth(i+1))
    yerror_u.append(h_error.GetBinErrorUp(i+1))
    yerror_d.append(h_error.GetBinErrorLow(i+1))
  gr = ROOT.TGraphAsymmErrors(len(x), np.array(x), np.array(y),np.array(xerror_l),np.array(xerror_r), np.array(yerror_d), np.array(yerror_u))
  
  DY_yield =round(DY.Integral(),1)
  signal_yield =round(signal.Integral(),1)
  WJet_yield =round(WJet.Integral(),1)
  TTto1L_yield =round(TTto1L.Integral(),1)
  TTto2L_yield =round(TTto2L.Integral(),1)
  VV_yield =round(VV.Integral(),1)
  VVV_yield =round(VVV.Integral(),1)
  SingleTop_yield =round(SingleTop.Integral(),1)
  TTV_yield =round(TTV.Integral(),1)
  TTVV_yield =round(TTVV.Integral(),1)
  TZq_yield =round(TZq.Integral(),1)
  QCD_yield =round(QCD.Integral(),1)
  Data_yield = round(Data.Integral())
  
  c = ROOT.TCanvas()
  pad1 = ROOT.TPad('pad1','',0.00, 0.22, 0.99, 0.99)
  pad2 = ROOT.TPad('pad1','',0.00, 0.00, 0.99, 0.22)
  pad1.SetBottomMargin(0.02);
  pad2.SetTopMargin(0.035);
  pad2.SetBottomMargin(0.45);
  pad1.Draw()
  pad2.Draw()
  pad1.cd()
  h_stack.Draw('HIST')
  Data.Draw("SAME pe")
  
  gr.SetFillColor(1)
  gr.SetFillStyle(3005)
  gr.Draw("SAME 2")

  set_axis(h_stack,'x', x_name, isenergy)

#  if 'DY_l1_pt' in x_name:set_axis(h_stack,'x', 'pt of leading lepton', True)
#  if 'DY_l1_eta' in x_name:set_axis(h_stack,'x', '#eta of leading lepton', False)
#  if 'DY_l1_phi' in x_name:set_axis(h_stack,'x', 'phi of leading lepton', False)
#  if 'DY_l2_pt' in x_name:set_axis(h_stack,'x', 'pt of subleading lepton', True)
#  if 'DY_l2_eta' in x_name:set_axis(h_stack,'x', '#eta of subleading lepton', False)
#  if 'DY_l2_phi' in x_name:set_axis(h_stack,'x', 'phi of subleading lepton', False)
#  if 'DY_z_mass' in x_name:set_axis(h_stack,'x', 'Z mass', True)
#  if 'DY_z_pt' in x_name:set_axis(h_stack,'x', 'Z pt', True)
#  if 'DY_z_eta' in x_name:set_axis(h_stack,'x', 'Z #eta', False)
#  if 'DY_z_phi' in x_name:set_axis(h_stack,'x', 'Z phi', False)

  set_axis(h_stack,'y', 'Event/Bin', False)
  
  CMSstyle.SetStyle(pad1)
  
  ##legend
  leg1 = ROOT.TLegend(0.68, 0.75, 0.94, 0.88)
  leg2 = ROOT.TLegend(0.44, 0.75, 0.64, 0.88)
  leg3 = ROOT.TLegend(0.17, 0.75, 0.40, 0.88)
  leg1.SetMargin(0.4)
  leg2.SetMargin(0.4)
  leg3.SetMargin(0.4)
  
  leg3.AddEntry(signal,'signal ['+str(signal_yield)+']','f')
  leg3.AddEntry(WJet,'WJet ['+str(WJet_yield)+']','f')
  leg3.AddEntry(DY,'DY ['+str(DY_yield)+']','f')
  leg3.AddEntry(gr,'Stat. unc','f')
  leg3.AddEntry(Data,'Data ['+str(Data_yield)+']','pe')
  leg2.AddEntry(SingleTop,'SingleTop ['+str(SingleTop_yield)+']','f')
  leg2.AddEntry(TTVV,'TTVV ['+str(TTVV_yield)+']','f')
  leg2.AddEntry(TTV,'TTV ['+str(TTV_yield)+']','f')
  leg2.AddEntry(TTto2L,'TTto2L ['+str(TTto2L_yield)+']','f')
  leg2.AddEntry(TTto1L,'TTto1L ['+str(TTto1L_yield)+']','f')
  leg1.AddEntry(QCD,'QCD ['+str(QCD_yield)+']','f')
  leg1.AddEntry(TZq,'TZq ['+str(TZq_yield)+']','f')
  leg1.AddEntry(VVV,'VVV ['+str(VVV_yield)+']','f')
  leg1.AddEntry(VV,'VV ['+str(VV_yield)+']','f')
  leg1.SetFillColor(ROOT.kWhite)
  leg1.Draw('same')
  leg2.SetFillColor(ROOT.kWhite);
  leg2.Draw('same');
  leg3.SetFillColor(ROOT.kWhite);
  leg3.Draw('same');
  
  pad2.cd()
  hMC = h_stack.GetStack().Last()
  hData = Data.Clone()
  hData.Divide(hMC)
  hData.SetMarkerStyle(20)
  hData.SetMarkerSize(0.85)
  hData.SetMarkerColor(1)
  hData.SetLineWidth(1)
  
  hData.GetYaxis().SetTitle("Data/Pred.")
  hData.GetXaxis().SetTitle(h_stack.GetXaxis().GetTitle())
  hData.GetYaxis().CenterTitle()
  hData.SetMaximum(1.5)
  hData.SetMinimum(0.5)
  hData.GetYaxis().SetNdivisions(4,kFALSE)
  hData.GetYaxis().SetTitleOffset(0.3)
  hData.GetYaxis().SetTitleSize(0.14)
  hData.GetYaxis().SetLabelSize(0.1)
  hData.GetXaxis().SetTitleSize(0.14)
  hData.GetXaxis().SetLabelSize(0.1)
  hData.Draw()
  
  c.Update()
  c.SaveAs(x_name+'.pdf')
  c.SaveAs(x_name+'.png')
  return c
  pad1.Close()
  pad2.Close()
  del hist_array

if __name__ == "__main__":
  start = time.time()
  start1 = time.clock() 
  plot()
  end = time.time()
  end1 = time.clock()
  print "wall time:", end-start
  print "process time:", end1-start1
