#include "ROOT/RDataFrame.hxx"
#include "TString.h"
#include "TFile.h"
#include "TH2D.h"
#include "TMath.h"
#include "TLorentzVector.h"
#include "ROOT/RVec.hxx"

const Double_t kPI = 3.141593;

using namespace ROOT::VecOps;
using rvec_f = const RVec<float> &;
using rvec_i = const RVec<int> &;

TFile*f_eleID=TFile::Open("eleIDSF.root");
TH2D*h2_eleID=(TH2D*)f_eleID->Get("EleIDSF");

TFile*f_muID=TFile::Open("muIDSF.root");
TH2D*h2_muID=(TH2D*)f_muID->Get("MuIDSF");

TFile*f_mutri=TFile::Open("TriggerSF_mu.root");
TH2D*h2_mutri=(TH2D*)f_mutri->Get("TriigerSF_mu");

TFile*f_eletri=TFile::Open("TriggerSF_ele.root");
TH2D*h2_eletri=(TH2D*)f_eletri->Get("TriigerSF_ele");

TFile*f_beff=TFile::Open("bEff.root");
TH2D*h2_beff_b=(TH2D*)f_beff->Get("Looseb");
TH2D*h2_beff_c=(TH2D*)f_beff->Get("Loosec");
TH2D*h2_beff_l=(TH2D*)f_beff->Get("Loosel");

float muIDSF(float pt1, float eta1, float pt2, float eta2){
  pt1 = pt1 > 150. ? 150. : pt1;
  pt2 = pt2 > 150. ? 150. : pt2;
  float l1_sf=h2_muID->GetBinContent(h2_muID->FindBin(fabs(eta1),pt1));
  float l2_sf=h2_muID->GetBinContent(h2_muID->FindBin(fabs(eta2),pt2));
  return l1_sf*l2_sf;
}

float eleIDSF(float pt1, float eta1, float pt2, float eta2){
  pt1 = pt1 > 100. ? 100. : pt1;
  pt2 = pt2 > 100. ? 100. : pt2;
  float l1_sf=h2_eleID->GetBinContent(h2_eleID->FindBin(fabs(eta1),pt1));
  float l2_sf=h2_eleID->GetBinContent(h2_eleID->FindBin(fabs(eta2),pt2));
  return l1_sf*l2_sf;
}

float muTriSF(float eta1, float eta2){
  float tri_sf=h2_mutri->GetBinContent(h2_mutri->FindBin(fabs(eta1),fabs(eta2)));
  return tri_sf;
}

float eleTriSF(float eta1, float eta2){
  float tri_sf=h2_eletri->GetBinContent(h2_eletri->FindBin(fabs(eta1),fabs(eta2)));
  return tri_sf;
}

float bSF(int n_tight_jet, rvec_i TightAK4Jet_id, rvec_i jetID, rvec_f pt, rvec_f eta, rvec_i flavor, rvec_f SFs, rvec_i bjetID, rvec_f drl1, rvec_f drl2){
  
  if (n_tight_jet==0) return 1;
  float sf_nume=1.;
  float sf_deno=1.;
  float eff_tmp;
  float pt_tmp=999.;
  int id_tmp;
  for(int i=0;i<n_tight_jet;i++){
    id_tmp=TightAK4Jet_id[i];
    if (jetID[id_tmp]<2 || pt[id_tmp]<30 || fabs(eta[id_tmp])>2.4 || drl1[i]<0.4 || drl2[i]<0.4) continue;
    if (pt[id_tmp]>1000) pt_tmp=999.;
    else pt_tmp=pt[id_tmp];
    float jet_scalefactor =  SFs[id_tmp];
    if (fabs(flavor[id_tmp])==5){
      eff_tmp=h2_beff_b->GetBinContent(h2_beff_b->FindBin(pt_tmp,fabs(eta[id_tmp])));
    }
    else if (fabs(flavor[id_tmp])==4){
      eff_tmp=h2_beff_c->GetBinContent(h2_beff_c->FindBin(pt_tmp,fabs(eta[id_tmp])));
    }
    else{
      eff_tmp=h2_beff_l->GetBinContent(h2_beff_l->FindBin(pt_tmp,fabs(eta[id_tmp])));
    }
    if (std::find(std::begin(bjetID), std::end(bjetID), id_tmp) != std::end(bjetID))    {
      sf_deno=sf_deno*eff_tmp;
      sf_nume=sf_nume*eff_tmp*jet_scalefactor;
    }
    else {
      sf_deno=sf_deno*(1.-eff_tmp);
      sf_nume=sf_nume*(1.-eff_tmp*jet_scalefactor);
    }; 
  }
  return sf_nume/sf_deno;
}
