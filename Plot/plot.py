import ROOT,sys,os
import numpy as np
from ROOT import kFALSE
import time

import CMSTDRStyle
#CMSTDRStyle.setTDRStyle().cd()
import CMSstyle
from array import array
ROOT.gROOT.SetBatch(True)

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

# XS: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageAt13TeV#ttH_Process
# BR: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBR
xs={
'QCD':239000,
'DY':6077.22,
'WJets':61526.7,
'TTto2L':88.3419,
'TTto1L':365.4574,
't_tch':136.02,
'tbar_tch':80.95,
'tW':35.85,
'tbarW':35.85,
'ttWtoLNu':0.1792,
'ttWtoQQ':0.3708,
'ttZ':0.2589,
'ttZtoQQ':0.6012,
'ttWW':0.007003,
'ttWZ':0.002453,
'ttZZ':0.001386,
'tZq':0.07561,
'ssWWew':0.0281,
'ssWWqcd':0.02391,
'WW_1L':50.85,
'WW_2L':11.09,
'WZ_3L':5.213,
'WZ_2L':9.146,
'WZ_1L':9.119,
'ZZ_2L':0.9738,
'WWW':0.2086,
'WWZ':0.1707,
'WZZ':0.05709,
'ZZZ':0.01476,
'GluGluHtoZZto2L2Q':0.106,
'GluGluHtoZZto2L2Nu':0.03,
'GluGluHtoWWto2L':0.5,
'VBFHtoZZto2L':0.018,
'VBFHtoWWto2L':0.091,
'WPHtoZZto2L':0.0041,
'WMHtoZZto2L':0.00255,
'ZHtoBBLL':0.07977,
'ZHtoZZto2L':0.0051,
'ggZHtoBB':0.071,
'ggZHtoWW':0.026,
'ttHtononBB':0.212,
'ttHtoBB':0.295
}

colors={
'SingleMuon':0,
'SingleEG':0,
'QCD':30,
'WJets':9,
'DY':2,
'TTto2L':5,
'TTto1L':4,
't_tch':3,
'tbar_tch':3,
'tW':3,
'tbarW':3,
'ttWtoLNu':3,
'ttWtoQQ':3,
'ttZ':3,
'ttZtoQQ':3,
'ttWW':3,
'ttWZ':3,
'ttZZ':3,
'tZq':3,
'ssWWew':3,
'ssWWqcd':3,
'WW_1L':3,
'WW_2L':3,
'WZ_3L':3,
'WZ_2L':3,
'WZ_1L':3,
'ZZ_2L':3,
'WWW':3,
'WWZ':3,
'WZZ':3,
'ZZZ':3,
'GluGluHtoZZto2L2Q':6,
'GluGluHtoZZto2L2Nu':6,
'GluGluHtoWWto2L':6,
'VBFHtoZZto2L':6,
'VBFHtoWWto2L':6,
'WPHtoZZto2L':6,
'WMHtoZZto2L':6,
'ZHtoBBLL':6,
'ZHtoZZto2L':6,
'ggZHtoBB':6,
'ggZHtoWW':6,
'ttHtononBB':6,
'ttHtoBB':6
}

DIRS = sys.argv[1]
VARYS = sys.argv[2]
YEAR = sys.argv[3]
BLIND = sys.argv[4]

lumi=1.0
if YEAR=='2016pre': lumi=19500
elif YEAR=='2016post': lumi=16800
elif YEAR=='2017': lumi=41480
elif YEAR=='2018': lumi=59700
else: raise ValueError("Please try UL year")

def plot():
  BASIC_PATH=os.getcwd()
  BASIC_PATH=BASIC_PATH+'/'+DIRS
  for root, dirs, files in os.walk(BASIC_PATH,topdown = False):
    samples_list_=files

  samples_list = [item for item in samples_list_ if 'slim' not in item]
#  print(samples_list)
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
    if VARYS=='ALL' and (name_tmp.split('_')[-1]=='CR' or name_tmp.split('_')[-1]=='SR'):
      histname_arr.append(name_tmp)
    if VARYS=='Btag' and name_tmp.split('_')[-1]=='Btag':
      histname_arr.append(name_tmp)
    elem = it.Next()

  fin.Close()

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
  
    if BLIND=='1':
      draw_plots(histos,histos_name,0,histname_arr[ihist],isenergy)
    else:
      draw_plots(histos,histos_name,1,histname_arr[ihist],isenergy)

def draw_plots(hist_array =[], hist_name =[], draw_data=0, x_name='', isenergy=False):

  DY = hist_array[1].Clone()
  DY.Reset()
  DY.SetFillColor(2)
  signal=DY.Clone()
  signal.SetFillColor(46)
  TTto2L=DY.Clone()
  TTto2L.SetFillColor(5)
  SMHiggs=DY.Clone()
  SMHiggs.SetFillColor(6)
  NonPrompt=DY.Clone()
  NonPrompt.SetFillColor(4)
  Others=DY.Clone()
  Others.SetFillColor(3)

  Data=DY.Clone()

  for ihist in range(0,len(hist_name)):
    if 'Single' in hist_name[ihist]:
      if 'Fake' in hist_name[ihist]:
        NonPrompt.Add(hist_array[ihist])
      elif not draw_data==0:
          Data.Add(hist_array[ihist])
    else:
      if colors[hist_name[ihist]]==2:
        DY.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==46:
        signal.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==4:
        NonPrompt.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==5:
        TTto2L.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==6:
        SMHiggs.Add(hist_array[ihist])
      if colors[hist_name[ihist]]==3:
        Others.Add(hist_array[ihist])

  Data.SetMarkerStyle(20)
  Data.SetMarkerSize(0.85)
  Data.SetMarkerColor(1)
  Data.SetLineWidth(1)


  h_stack = ROOT.THStack()
  h_stack.Add(DY)
  h_stack.Add(TTto2L)
  h_stack.Add(NonPrompt)
  h_stack.Add(SMHiggs)
  h_stack.Add(Others)
#  h_stack.Add(signal)
  max_yields = 0
  Nbins=h_stack.GetStack().Last().GetNbinsX()
  for i in range(1,Nbins+1):
    max_yields_temp = h_stack.GetStack().Last().GetBinContent(i)
    if max_yields_temp>max_yields:max_yields=max_yields_temp
  
  max_yields_data = 0
  for i in range(1,Nbins+1):
    max_yields_data_temp = Data.GetBinContent(i)
    if max_yields_data_temp>max_yields_data:max_yields_data=max_yields_data_temp
  
  h_stack.SetMaximum(max(max_yields, max_yields_data)*2.2)

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
  TTto2L_yield =round(TTto2L.Integral(),1)
  NonPrompt_yield =round(NonPrompt.Integral(),1)
  SMHiggs_yield =round(SMHiggs.Integral(),1)
  Others_yield =round(Others.Integral(),1)
  Data_yield = round(Data.Integral())
  
  ROOT.gStyle.SetCanvasBorderMode(0);
  ROOT.gStyle.SetCanvasColor(ROOT.kWhite);
  ROOT.gStyle.SetCanvasDefH(600); #Height of canvas
  ROOT.gStyle.SetCanvasDefW(600); #Width of canvas
  ROOT.gStyle.SetCanvasDefX(0);   #Position on screen
  ROOT.gStyle.SetCanvasDefY(0);
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

  set_axis(h_stack,'y', 'Event/Bin', False)
  
  CMSstyle.SetStyle(pad1)
  
  ##legend
  leg1 = ROOT.TLegend(0.6, 0.65, 0.94, 0.88)
  leg1.SetMargin(0.4)
  
  leg1.AddEntry(DY,'DY ['+str(DY_yield)+']','f')
  leg1.AddEntry(TTto2L,'TTto2L ['+str(TTto2L_yield)+']','f')
  leg1.AddEntry(NonPrompt,'NonPrompt ['+str(NonPrompt_yield)+']','f')
  leg1.AddEntry(SMHiggs,'SMHiggs ['+str(SMHiggs_yield)+']','f')
  leg1.AddEntry(Others,'Others ['+str(Others_yield)+']','f')
  leg1.AddEntry(gr,'Stat. unc','f')
  leg1.SetFillColor(ROOT.kWhite)
  leg1.Draw('same')
  
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
  plot()
