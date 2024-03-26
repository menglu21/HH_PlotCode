import ROOT
import time
import os
import math
from math import sqrt
import argparse

HH_header_path = os.path.join("HH.h")
ROOT.gInterpreter.Declare('#include "{}"'.format(HH_header_path))

RDataFrame = ROOT.RDataFrame

def main():
  usage = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(usage)
  parser.add_argument('-i', '--inputs',dest='inputs',help='input root file',default='dummy.root')
  parser.add_argument('-r', '--region',dest='region',help='SR or which CR',default='onelep_b_region')
  parser.add_argument('-c', '--channel',dest='channel',help='ele or muon channel',default='muon')
  parser.add_argument('-t', '--category',dest='category',help='category of fatjet and ak4jet',default='2F0R')
  parser.add_argument('-p', '--process',dest='process',help='process name used to decide which filter to be used',default='TTto2L')
  #2F0R, HF2R, ZF2R, 0F4R
  args = parser.parse_args()
  inputroot=args.inputs
  output_name='output.root'
  regions=args.region
  channel=args.channel
  category=args.category
  process=args.process
  HH_Analysis(inputroot,output_name,regions,channel,category,process)

def overunder_flowbin(h1):
  h1.SetBinContent(1,h1.GetBinContent(0)+h1.GetBinContent(1))
  h1.SetBinError(1,sqrt(h1.GetBinError(0)*h1.GetBinError(0)+h1.GetBinError(1)*h1.GetBinError(1)))
  h1.SetBinContent(h1.GetNbinsX(),h1.GetBinContent(h1.GetNbinsX())+h1.GetBinContent(h1.GetNbinsX()+1))
  h1.SetBinError(h1.GetNbinsX(),sqrt(h1.GetBinError(h1.GetNbinsX())*h1.GetBinError(h1.GetNbinsX())+h1.GetBinError(h1.GetNbinsX()+1)*h1.GetBinError(h1.GetNbinsX()+1)))
  return h1

def mc_trigger(df):
  all_trigger = df.Filter("HLT_IsoMu27 || HLT_Mu50 || HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 || HLT_passEle32WPTight || HLT_Ele35_WPTight_Gsf || HLT_Ele38_WPTight_Gsf || HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ || HLT_DoubleEle33_CaloIdL_MW")
  return all_trigger

def ele_trigger(df):
  ele_trigger = df.Filter("HLT_passEle32WPTight || HLT_Ele35_WPTight_Gsf || HLT_Ele38_WPTight_Gsf || HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ || HLT_DoubleEle33_CaloIdL_MW")
  return ele_trigger

def muon_trigger(df):
  mu_trigger = df.Filter("HLT_IsoMu27 || HLT_Mu50 || HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8")
  return mu_trigger



MET_filter = "Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_eeBadScFilter && Flag_ecalBadCalibFilter"

Type_I = ['ttHtoBB', 'ttHtononBB'] # use lhe_nlepton>1
Type_II = ['ZZZ', 'WZZ', 'WWZ', 'WWW', 'ttWW', 'ttWZ', 'ttZZ', 'ttWtoQQ', 'ttWtoLNu', 'tbarW', 'tW'] # use nGenDressedLepton>1
# other MC bkg already have at least two prompt leptons, no need to select

def HH_Analysis(inputfile,outputname,regions,channel,category,process):

  ismc=False

  #histograms name
  if regions=="TT" or regions=="TTss":
    hists_name = {
    'l1_pt':[50,0,250],
    'l1_eta':[20,-2.5,2.5],
    'l1_phi':[20,-4,4],
    'l2_pt':[22,10,120],
    'l2_eta':[20,-2.5,2.5],
    'l2_phi':[20,-4,4],
    'drll':[50,0,5],
    'detall':[50,0,5],
    'dphill':[40,-4,4],
    'zlep_pt':[50,0,250],
    'zlep_eta':[40,-5,5],
    'zlep_phi':[20,-4,4],
    'zlep_mass':[50,50,400],
    'met_user':[50,0,250],
    'met_phi_user':[20,-4,4],
    'TT_Lb1_pt':[30,0,300],
    'TT_Lb1_eta':[20,-2.5,2.5],
    'TT_Lb1_phi':[20,-4,4],
    'TT_Lb1_mass':[25,0,50],
    'TT_Lb2_pt':[20,0,200],
    'TT_Lb2_eta':[20,-2.5,2.5],
    'TT_Lb2_phi':[20,-4,4],
    'TT_Lb2_mass':[15,0,30],
    'TT_Lmbb':[40,0,600],
    'TT_Lb1_drl1':[25,0,5],
    'TT_Lb1_drl2':[25,0,5],
    'TT_Lb2_drl1':[25,0,5],
    'TT_Lb2_drl2':[25,0,5],
    'nFatJet':[10,0,10],
    'nJet':[10,0,10],
    'nJetNoVlep':[10,0,10],
    'nFatJetNoVlep':[10,0,10],
    'nTightAK4JetCRall':[10,0,10],
    'nTightAK4JetCRall_b_DeepJetL':[10,0,10],
    'nTightAK4JetCRall_b_DeepJetM':[10,0,10],
    'nTightAK4Jet':[10,0,10]
    }
  if regions=="lowMTT":
    hists_name = {
    'l1_pt':[50,0,250],
    'l1_eta':[20,-2.5,2.5],
    'l1_phi':[20,-4,4],
    'l2_pt':[22,10,120],
    'l2_eta':[20,-2.5,2.5],
    'l2_phi':[20,-4,4],
    'drll':[50,0,5],
    'detall':[50,0,5],
    'dphill':[40,-4,4],
    'zlep_pt':[50,0,250],
    'zlep_eta':[40,-5,5],
    'zlep_phi':[20,-4,4],
    'zlep_mass':[7,0,105],
    'met_user':[50,0,250],
    'met_phi_user':[20,-4,4],
    'TT_Lb1_pt':[30,0,300],
    'TT_Lb1_eta':[20,-2.5,2.5],
    'TT_Lb1_phi':[20,-4,4],
    'TT_Lb1_mass':[25,0,50],
    'TT_Lb2_pt':[20,0,200],
    'TT_Lb2_eta':[20,-2.5,2.5],
    'TT_Lb2_phi':[20,-4,4],
    'TT_Lb2_mass':[15,0,30],
    'TT_Lmbb':[40,0,600],
    'TT_Lb1_drl1':[25,0,5],
    'TT_Lb1_drl2':[25,0,5],
    'TT_Lb2_drl1':[25,0,5],
    'TT_Lb2_drl2':[25,0,5],
    'nFatJet':[10,0,10],
    'nJet':[10,0,10],
    'nJetNoVlep':[10,0,10],
    'nFatJetNoVlep':[10,0,10],
    'nTightAK4JetCRall':[10,0,10],
    'nTightAK4JetCRall_b_DeepJetL':[10,0,10],
    'nTightAK4JetCRall_b_DeepJetM':[10,0,10],
    'nTightAK4Jet':[10,0,10]
    }
  elif 'DY2J' in regions:
    hists_name = {
    'l1_pt':[28,10,150],
    'l1_eta':[30,-3,3],
    'l1_phi':[40,-4,4],
    'l2_pt':[22,10,120],
    'l2_eta':[30,-3,3],
    'l2_phi':[40,-4,4],
    'drll':[50,0,5],
    'detall':[50,0,5],
    'dphill':[40,-4,4],
    'zlep_pt':[50,0,250],
    'zlep_eta':[50,-5,5],
    'zlep_phi':[40,-4,4],
    'zlep_mass':[80,70,110],
    'met_user':[60,0,300],
    'met_phi_user':[40,-4,4],
    'DY_j1_pt':[40,0,400],
    'DY_j1_eta':[60,-3,3],
    'DY_j1_phi':[40,-4,4],
    'DY_j1_mass':[50,0,50],
    'DY_j2_pt':[20,0,200],
    'DY_j2_eta':[60,-3,3],
    'DY_j2_phi':[50,-4,4],
    'DY_j2_mass':[30,0,30],
    'DY_mjj':[50,0,1000],
    'DY_j1_drl1':[30,0,6],
    'DY_j1_drl2':[30,0,6],
    'DY_j2_drl1':[30,0,6],
    'DY_j2_drl2':[30,0,6],
    'nFatJet':[10,0,10],
    'nJet':[10,0,10],
    'nJetNoVlep':[10,0,10],
    'nFatJetNoVlep':[10,0,10],
    'nTightAK4JetCRall':[10,0,10],
    'nTightAK4JetCRall_b_DeepJetL':[10,0,10],
    'nTightAK4JetCRall_b_DeepJetM':[10,0,10],
    'nTightAK4Jet':[10,0,10]
    }
  elif 'DY' in regions:
    hists_name = {
    'l1_pt':[28,10,150],
    'l1_eta':[30,-3,3],
    'l1_phi':[40,-4,4],
    'l2_pt':[22,10,120],
    'l2_eta':[30,-3,3],
    'l2_phi':[40,-4,4],
    'drll':[50,0,5],
    'detall':[50,0,5],
    'dphill':[40,-4,4],
    'zlep_pt':[50,0,250],
    'zlep_eta':[50,-5,5],
    'zlep_phi':[40,-4,4],
    'zlep_mass':[80,70,110],
    'met_user':[60,0,300],
    'met_phi_user':[40,-4,4],
    'nFatJet':[10,0,10],
    'nJet':[10,0,10],
    'nJetNoVlep':[10,0,10],
    'nFatJetNoVlep':[10,0,10],
    'nTightAK4JetCRall':[10,0,10],
    'nTightAK4JetCRall_b_DeepJetL':[10,0,10],
    'nTightAK4JetCRall_b_DeepJetM':[10,0,10],
    'nTightAK4Jet':[10,0,10]
    }
  elif 'SR2F' in regions:
    hists_name = {
    'l1_pt':[3,0,120],
    'l1_eta':[4,-2.5,2.5],
    'l1_phi':[4,-4,4],
    'l2_pt':[3,0,90],
    'l2_eta':[4,-2.5,2.5],
    'l2_phi':[4,-4,4],
    'drll':[3,0,3],
    'detall':[4,0,2],
    'dphill':[4,-4,4],
    'zlep_pt':[4,0,120],
    'zlep_eta':[4,-4,4],
    'zlep_phi':[4,-4,4],
    'zlep_mass':[6,0,120],
    'met_user':[4,0,200],
    'met_phi_user':[4,-4,4],
    'nTightFatJet':[5,0,5],
    'H_AK8Jet_pt':[4,200,600],
    'H_AK8Jet_eta':[6,-3,3],
    'H_AK8Jet_phi':[4,-4,4],
    'H_AK8Jet_mass':[5,0,100],
    'H_AK8Jet_PNmass':[5,0,100],
    'H_AK8Jet_SDmass':[5,0,100],
    'H_AK8Jet_drl1':[4,0,4],
    'H_AK8Jet_drl2':[4,0,4],
    'Z_AK8Jet_pt':[4,200,600],
    'Z_AK8Jet_eta':[6,-3,3],
    'Z_AK8Jet_phi':[4,-4,4],
    'Z_AK8Jet_mass':[6,0,120],
    'Z_AK8Jet_drl1':[4,0,4],
    'Z_AK8Jet_drl2':[4,0,4]
    }
  elif 'SRHF' in regions:
    hists_name = {
    'l1_pt':[3,0,120],
    'l1_eta':[4,-2.5,2.5],
    'l1_phi':[4,-4,4],
    'l2_pt':[3,0,90],
    'l2_eta':[4,-2.5,2.5],
    'l2_phi':[4,-4,4],
    'drll':[3,0,3],
    'detall':[2,0,2],
    'dphill':[2,-4,4],
    'zlep_pt':[4,0,160],
    'zlep_eta':[2,-2,2],
    'zlep_phi':[4,-4,4],
    'zlep_mass':[6,0,120],
    'met_user':[4,0,200],
    'met_phi_user':[4,-4,4],
    'nTightFatJet':[5,0,5],
    'H_AK8Jet_pt':[3,200,500],
    'H_AK8Jet_eta':[4,-2,2],
    'H_AK8Jet_phi':[6,-3,3],
    'H_AK8Jet_mass':[5,0,100],
    'H_AK8Jet_PNmass':[5,0,100],
    'H_AK8Jet_SDmass':[5,0,100],
    'H_AK8Jet_drl1':[4,0,4],
    'H_AK8Jet_drl2':[4,0,4]
#    'Z_AK4Jet1_pt':[16,200,1000],
#    'Z_AK4Jet1_eta':[20,-5,5],
#    'Z_AK4Jet1_phi':[20,-4,4],
#    'Z_AK4Jet1_mass':[50,0,250],
#    'Z_AK4Jet2_pt':[16,200,1000],
#    'Z_AK4Jet2_eta':[20,-5,5],
#    'Z_AK4Jet2_phi':[20,-4,4],
#    'Z_AK4Jet2_mass':[50,0,250],
#    'Z_AK4Jet1_drl1':[50,0,10],
#    'Z_AK4Jet1_drl2':[50,0,10],
#    'Z_AK4Jet2_drl1':[50,0,10],
#    'Z_AK4Jet2_drl2':[50,0,10],
#    'Z_AK4Jet_mjj':[100,0,1000],
#    'Z_AK4Jet_drjj':[50,0,10]
    }
  elif 'SRZF' in regions:
    hists_name = {
    'l1_pt':[11,10,120],
    'l1_eta':[10,-2.5,2.5],
    'l1_phi':[10,-4,4],
    'l2_pt':[8,10,90],
    'l2_eta':[10,-2.5,2.5],
    'l2_phi':[10,-4,4],
    'drll':[10,0,4],
    'detall':[10,0,2],
    'dphill':[10,-4,4],
    'zlep_pt':[10,0,200],
    'zlep_eta':[12,-3,3],
    'zlep_phi':[10,-4,4],
    'zlep_mass':[12,0,120],
    'met_user':[10,0,200],
    'met_phi_user':[10,-4,4],
    'nTightFatJet':[5,0,5],
    'h_j1_pt':[6,200,500],
    'h_j1_eta':[6,-3,3],
    'h_j1_phi':[10,-4,4],
    'h_j1_mass':[5,0,50],
    'h_j2_pt':[6,200,500],
    'h_j2_eta':[6,-3,3],
    'h_j2_phi':[10,-4,4],
    'h_j2_mass':[10,0,4],
    'h_j1_drl1':[10,0,4],
    'h_j1_drl2':[10,0,4],
    'h_j2_drl1':[10,0,4],
    'h_j2_drl2':[10,0,4],
    'h_mjj':[7,90,160],
    'h_dRjj':[8,0,4],
    'Z_AK8Jet_pt':[10,200,700],
    'Z_AK8Jet_eta':[12,-3,3],
    'Z_AK8Jet_phi':[16,-4,4],
    'Z_AK8Jet_mass':[12,0,120],
    'Z_AK8Jet_drl1':[8,0,4],
    'Z_AK8Jet_drl2':[8,0,4]
    }
  elif 'SR0F' in regions:
    hists_name = {
    'l1_pt':[11,10,120],
    'l1_eta':[10,-2.5,2.5],
    'l1_phi':[20,-4,4],
    'l2_pt':[10,10,60],
    'l2_eta':[10,-2.5,2.5],
    'l2_phi':[20,-4,4],
    'drll':[20,0,4],
    'detall':[20,0,2.5],
    'dphill':[40,-4,4],
    'zlep_pt':[20,0,200],
    'zlep_eta':[20,-4,4],
    'zlep_phi':[20,-4,4],
    'zlep_mass':[20,0,120],
    'met_user':[10,0,200],
    'met_phi_user':[20,-4,4],
    'nTightFatJet':[5,0,5],
    'h_j1_pt':[15,0,300],
    'h_j1_eta':[12,-3,3],
    'h_j1_phi':[20,-4,4],
    'h_j1_mass':[10,0,30],
    'h_j2_pt':[10,0,200],
    'h_j2_eta':[12,-3,3],
    'h_j2_phi':[20,-4,4],
    'h_j2_mass':[10,0,20],
    'h_j1_drl1':[10,0,4],
    'h_j1_drl2':[10,0,4],
    'h_j2_drl1':[10,0,4],
    'h_j2_drl2':[10,0,4],
    'h_mjj':[20,0,200],
    'h_dRjj':[10,0,4]
#    'Z_AK4Jet1_pt':[16,200,1000],
#    'Z_AK4Jet1_eta':[20,-5,5],
#    'Z_AK4Jet1_phi':[20,-4,4],
#    'Z_AK4Jet1_mass':[50,0,250],
#    'Z_AK4Jet2_pt':[16,200,1000],
#    'Z_AK4Jet2_eta':[20,-5,5],
#    'Z_AK4Jet2_phi':[20,-4,4],
#    'Z_AK4Jet2_mass':[50,0,250],
#    'Z_AK4Jet1_drl1':[50,0,10],
#    'Z_AK4Jet1_drl2':[50,0,10],
#    'Z_AK4Jet2_drl1':[50,0,10],
#    'Z_AK4Jet2_drl2':[50,0,10],
#    'Z_AK4Jet_mjj':[100,0,1000],
#    'Z_AK4Jet_drjj':[50,0,10]
    }

#    'n_bjet_DeepB_M':[5,0,5],
#    'n_bjet_DeepB_L':[10,0,10],
#    'n_tight_nob':[10,0,10],
#    'HT':[40,0,1000],
#    'nTightAK4Jet':[10,0,10],
#    'h_j1_pt':[25,0,500],
#    'h_j1_eta':[20,-5,5],
#    'h_j1_phi':[20,-4,4],
#    'h_j1_mass':[20,0,40],
#    'h_j2_pt':[15,0,300],
#    'h_j2_eta':[20,-5,5],
#    'h_j2_phi':[20,-4,4],
#    'h_j2_mass':[20,0,40],
#    'h_mjj':[20,0,300],
#    'h_detajj':[10,0,3],
#    'h_dRjj':[10,0,4],
#    'h_dphijj':[20,-4,4]
   #'zhad_j1_pt':[25,0,500],
   #'zhad_j1_eta':[20,-5,5],
   #'zhad_j1_phi':[20,-4,4],
   #'zhad_j1_mass':[20,0,40],
   #'zhad_j2_pt':[15,0,300],
   #'zhad_j2_eta':[20,-5,5],
   #'zhad_j2_phi':[20,-4,4],
   #'zhad_j2_mass':[20,0,40],
   #'zhad_mjj':[20,0,300],
   #'zhad_detajj':[10,0,3],
   #'zhad_dRjj':[10,0,4],
   #'zhad_dphijj':[20,-4,4],
   #'mass_zhad_zlep':[20,0,600]

  hists_keys=list(hists_name.keys())
  hists_bins=[hists_name[x][0] for x in hists_keys]
  hists_edgeLow=[hists_name[x][1] for x in hists_keys]
  hists_edgeHigh=[hists_name[x][2] for x in hists_keys]
  
  HIST_names=hists_keys[:]
  HIST_bins=hists_bins[:]
  HIST_edgeLow=hists_edgeLow[:]
  HIST_edgeHigh=hists_edgeHigh[:]

  Filter=""

  if regions=="TT":
    if channel=='ele':
#      Filter="zlep_mass>105 && l1_pt>25 && l2_pt>15 && lep_2G0F==1 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nTightAK4JetCRall>1 && nTightAK4JetCRall_b_DeepJetL>1 && TT_Lb1_pt>0 && TT_Lb2_pt>0 && met_user>50"
      Filter="zlep_mass>105 && l1_pt>25 && l2_pt>15 && lep_2G0F==1 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nTightAK4JetCRall>1 && nTightAK4JetCRall_b_DeepJetL>1 && TT_Lb1_pt>0 && TT_Lb2_pt>0"
    else:
#      Filter="zlep_mass>105 && l1_pt>20 && l2_pt>12 && lep_2G0F==1 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nTightAK4JetCRall>1 && nTightAK4JetCRall_b_DeepJetL>1 && TT_Lb1_pt>0 && TT_Lb2_pt>0 && met_user>50"
      Filter="zlep_mass>105 && l1_pt>20 && l2_pt>12 && lep_2G0F==1 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nTightAK4JetCRall>1 && nTightAK4JetCRall_b_DeepJetL>1 && TT_Lb1_pt>0 && TT_Lb2_pt>0 && met_user>50"

  if regions=="lowMTT":
    if channel=='ele':
      Filter="zlep_mass<105 && l1_pt>25 && l2_pt>15 && lep_2G0F==1 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nTightAK4JetCRall>1 && nTightAK4JetCRall_b_DeepJetL>1"
    else:
      Filter="zlep_mass<105 && l1_pt>20 && l2_pt>12 && lep_2G0F==1 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nTightAK4JetCRall>1 && nTightAK4JetCRall_b_DeepJetL>1"

  if regions=="TTss":
    if channel=='ele':
      Filter="zlep_mass>105 && l1_pt>25 && l2_pt>15 && lep_2G0F==1 && ee_channel && IsSS && nLooseMuon==0 && nLooseElectron==0 && nTightAK4JetCRall>1 && nTightAK4JetCRall_b_DeepJetM>1"
    else:
      Filter="zlep_mass>105 && met_user>100 && nTightAK4JetCRall_b_DeepJetM>1 && IsSS && l1_pt>20 && l2_pt>12 && mm_channel && nLooseMuon==0 && nLooseElectron==0 && lep_2G0F==1"

  if regions=="DY2J":
    if channel=='ele':
      Filter="zlep_mass>75 && zlep_mass<105 && l1_pt>25 && l2_pt>15 && lep_2G0F==1 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nTightAK4JetCRall>1"
    else:
      Filter="zlep_mass>75 && zlep_mass<105 && l1_pt>20 && l2_pt>12 && lep_2G0F==1 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nTightAK4JetCRall>1"

  if regions=="DY":
    if channel=='ele':
      Filter="zlep_mass>75 && zlep_mass<105 && l1_pt>25 && l2_pt>15 && lep_2G0F==1 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
    else:
      Filter="zlep_mass>75 && zlep_mass<105 && l1_pt>20 && l2_pt>12 && lep_2G0F==1 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"

  if regions=="SR2F":
    if channel=='ele':
      if process in Type_I:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && lhe_nlepton>1"
      elif process in Type_II:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nGenDressedLepton>1"
      elif not 'Single' in process:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      elif not 'Fake' in process:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      else:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && (lep_1G1F==1 || lep_0G2F==1) && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"

    else:
      if process in Type_I:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && lhe_nlepton>1"
      elif process in Type_II:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nGenDressedLepton>1"
      elif not 'Single' in process:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      elif not 'Fake' in process:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      else:
        Filter="HZ_2F0R && H_AK8Jet_pt>0 && Z_AK8Jet_pt>0 && zlep_mass<105 && (lep_1G1F==1 || lep_0G2F==1) && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"

  if regions=="SRHF":
    if channel=='ele':
      if process in Type_I:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && lhe_nlepton>1"
      elif process in Type_II:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nGenDressedLepton>1"
      elif not 'Single' in process:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      elif not 'Fake' in process:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      else:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && (lep_1G1F==1 || lep_0G2F==1) && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"

    else:
      if process in Type_I:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && lhe_nlepton>1"
      elif process in Type_II:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nGenDressedLepton>1"
      elif not 'Single' in process:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      elif not 'Fake' in process:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      else:
        Filter="HZ_1F2R && H_AK8Jet_pt>0 && nzhad>0 && zlep_mass<105 && (lep_1G1F==1 || lep_0G2F==1) && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"

  if regions=="SRZF":
    if channel=='ele':
      if process in Type_I:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && lhe_nlepton>1"
      elif process in Type_II:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nGenDressedLepton>1"
      elif not 'Single' in process:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      elif not 'Fake' in process:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      else:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && (lep_1G1F==1 || lep_0G2F==1) && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"

    else:
      if process in Type_I:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && lhe_nlepton>1"
      elif process in Type_II:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nGenDressedLepton>1"
      elif not 'Single' in process:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      elif not 'Fake' in process:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      else:
        Filter="HZ_1F2R && Z_AK8Jet_pt>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && (lep_1G1F==1 || lep_0G2F==1) && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"

  if regions=="SR0F":
    if channel=='ele':
      if process in Type_I:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && lhe_nlepton>1"
      elif process in Type_II:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nGenDressedLepton>1"
      elif not 'Single' in process:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      elif not 'Fake' in process:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      else:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && (lep_1G1F==1 || lep_0G2F==1) && l1_pt>25 && l2_pt>15 && ee_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"

    else:
      if process in Type_I:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && lhe_nlepton>1"
      elif process in Type_II:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0 && nGenDressedLepton>1"
      elif not 'Single' in process:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      elif not 'Fake' in process:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && lep_2G0F==1 && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"
      else:
        Filter="HZ_0F4R && nzhad>0 && h_j1_pt>0 && h_j2_pt>0 && zlep_mass<105 && (lep_1G1F==1 || lep_0G2F==1) && l1_pt>20 && l2_pt>12 && mm_channel && !IsSS && nLooseMuon==0 && nLooseElectron==0"


  fout = ROOT.TFile.Open(outputname,'recreate')

  filein=ROOT.TFile.Open(inputfile)
  fout.cd()
  if not 'Single' in inputfile:
    hweight=ROOT.TH1D()
    hweight=filein.Get("nEventsGenWeighted")
    hweight.Write()
    ismc=True
  filein.Close()

  df_histosnoSF=[]
  df_histosID=[]
  df_histos=[]
  if regions=="TT" or regions=='TTss' or regions=='lowMTT' or regions=='SR0F' or regions=='SRZF':
    df_histosBtag=[]

  df_tree_ = ROOT.RDataFrame("Events", inputfile)
  if ismc: df_tree = mc_trigger(df_tree_)
  else:
    if channel=='muon': df_tree = muon_trigger(df_tree_)
    if channel=='ele': df_tree = ele_trigger(df_tree_)
  df_filter_ = df_tree.Filter(MET_filter)
  df_filter = df_filter_.Filter(Filter)

  filter_event = ""

  if (regions=="TT" or regions=='TTss' or regions=='lowMTT' or regions=='SR0F' or regions=='SRZF') and ismc:
    df_filter = df_filter.Define("btagSF","bSF(nTightAK4Jet,TightAK4Jet_id, JetNoVlep_jetId, JetNoVlep_pt_nom, JetNoVlep_eta, JetNoVlep_hadronFlavour, JetNoVlep_btagSF_deepjet_L, TightAK4Jet_b_DeepJetL_id, TightAK4Jet_drl1, TightAK4Jet_drl2)")

  if channel=='ele':
    df_filter = df_filter.Define("lepIDiso","eleIDSF(l1_pt,l1_eta,l2_pt,l2_eta)")
    df_filter = df_filter.Define("lepTri","eleTriSF(l1_eta,l2_eta)")
    df_filter = df_filter.Define("lep1relPt","Electron_jetPtRelv2[GoodElectron_id[0]]")
    df_filter = df_filter.Define("lep2relPt","Electron_jetPtRelv2[GoodElectron_id[1]]")
    if (not 'MET' in inputfile) and (not 'Single' in inputfile):
      df_filter = df_filter.Define("elereco1","Electron_RECO_SF[GoodElectron_id[0]]").Define("elereco2","Electron_RECO_SF[GoodElectron_id[1]]")

    filter_event = ""

  if channel=='muon':
    df_filter = df_filter.Define("lepIDiso","muIDSF(l1_pt,l1_eta,l2_pt,l2_eta)")
    df_filter = df_filter.Define("lepTri","muTriSF(l1_eta,l2_eta)")
    filter_event = ""

  if "Fake" in process:
    if channel=='ele':
      df_filter = df_filter.Define("fakeweight","fakelepweight_ee(zlep_mass)")
    if channel=='muon':
      df_filter = df_filter.Define("fakeweight","fakelepweight_mm(zlep_mass)")

  df_event=df_filter

  if ismc:
    if channel=='ele':
      df_event = df_event.Define('genweightnoSF','puWeight*L1PreFiringWeight_Nom*genWeight/abs(genWeight)')
      df_event = df_event.Define('genweightID','puWeight*L1PreFiringWeight_Nom*lepIDiso*elereco1*elereco2*genWeight/abs(genWeight)')
      df_event = df_event.Define('genweight','puWeight*L1PreFiringWeight_Nom*lepIDiso*lepTri*elereco1*elereco2*genWeight/abs(genWeight)')
      if regions=="TT" or regions=='TTss' or regions=='lowMTT' or regions=='SR0F' or regions=='SRZF':
        df_event = df_event.Define('genweightBtag','puWeight*L1PreFiringWeight_Nom*lepIDiso*lepTri*elereco1*elereco2*btagSF*genWeight/abs(genWeight)')
    if channel=='muon':
      df_event = df_event.Define('genweightnoSF','puWeight*L1PreFiringWeight_Nom*genWeight/abs(genWeight)')
      df_event = df_event.Define('genweightID','puWeight*L1PreFiringWeight_Nom*lepIDiso*genWeight/abs(genWeight)')
      df_event = df_event.Define('genweight','puWeight*L1PreFiringWeight_Nom*lepIDiso*lepTri*genWeight/abs(genWeight)')
      if regions=="TT" or regions=='TTss' or regions=='lowMTT' or regions=='SR0F' or regions=='SRZF':
        df_event = df_event.Define('genweightBtag','puWeight*L1PreFiringWeight_Nom*lepIDiso*lepTri*btagSF*genWeight/abs(genWeight)')
  elif 'Fake' in process:
    df_event = df_event.Define('Fakeweight','fakeweight')


  # further cuts
  #Filters_TT1L = "met_user>50 && mjj_nob>60 && mjj_nob<100"
  Filters_signal = ""

  for i in range(0,len(HIST_names)):
    if ismc:
      df_histonoSF = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category+'_noSF','',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i],'genweightnoSF')
      df_histoID = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category+'_ID','',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i],'genweightID')
      df_histo = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category,'',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i],'genweight')
      if regions=="TT" or regions=='TTss' or regions=='lowMTT' or regions=='SR0F' or regions=='SRZF':
        df_histoBtag = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category+'_Btag','',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i],'genweightBtag')
    elif 'Fake' in process:
      df_histonoSF = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category+'_noSF','',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i], 'Fakeweight')
      df_histoID = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category+'_ID','',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i], 'Fakeweight')
      df_histo = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category,'',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i], 'Fakeweight')
      if regions=="TT" or regions=='TTss' or regions=='lowMTT' or regions=='SR0F' or regions=='SRZF':
        df_histoBtag = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category+'_Btag','',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i], 'Fakeweight')

    else:
      df_histonoSF = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category+'_noSF','',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i])
      df_histoID = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category+'_ID','',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i])
      df_histo = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category,'',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i])
      if regions=="TT" or regions=='TTss' or regions=='lowMTT' or regions=='SR0F' or regions=='SRZF':
        df_histoBtag = df_event.Histo1D((HIST_names[i]+'_'+channel+'_'+category+'_Btag','',HIST_bins[i],HIST_edgeLow[i],HIST_edgeHigh[i]), HIST_names[i])

    df_histosnoSF.append(df_histonoSF)
    df_histosID.append(df_histoID)
    df_histos.append(df_histo)
    if regions=="TT" or regions=='TTss' or regions=='lowMTT' or regions=='SR0F' or regions=='SRZF':
      df_histosBtag.append(df_histoBtag)


  fout.cd()
  for ij in range(0,len(HIST_names)):
    h_tempnoSF = df_histosnoSF[ij].GetValue()
    h_tempnoSF.Write()
    h_tempID = df_histosID[ij].GetValue()
    h_tempID.Write()
    h_temp = df_histos[ij].GetValue()
    h_temp.Write()
    if regions=="TT" or regions=='TTss' or regions=='lowMTT' or regions=='SR0F' or regions=='SRZF':
      h_tempBtag = df_histosBtag[ij].GetValue()
      h_tempBtag.Write()

  fout.Close()

if __name__ == "__main__":
  start = time.time()
  start1 = time.process_time() 
  print("Job starts")
  main()
  end = time.time()
  end1 = time.process_time()
  print("wall time:", end-start)
  print("process time:", end1-start1)

