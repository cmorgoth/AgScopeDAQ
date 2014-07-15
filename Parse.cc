#include <vector>
#include <iostream>
#include <fstream>
#include <string>
#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TROOT.h"
#include <stdlib.h>     /* atof */
#include <math.h> 

#ifdef __MAKECINT__
#pragma link C++ class vector<float>+;
#endif


int main(){
  
  gROOT->Reset();
  gROOT->ProcessLine("#include <vector>");
  std::cout.precision(12);
  std::vector<double>   *Amp = new std::vector<double>();
  std::vector<double>   *Time = new std::vector<double>();
  std::vector<double>   *Amp2 = new std::vector<double>();
  std::vector<double>   *Time2 = new std::vector<double>();

  TTree* t = new TTree("outTree","CPT");
  
  int evt = 0;
  t->Branch("Evt", &evt,"Evt/I");
  t->Branch("Amp", "std::vector<double>*", Amp);
  t->Branch("Time", "std::vector<double>*" ,Time);
  t->Branch("Amp2", "std::vector<double>*", Amp2);
  t->Branch("Time2", "std::vector<double>*", Time2);

  std::ifstream lis("list_MCP_dual.txt", std::ifstream::in);
  char fname[100];
  std::string ff;
  
  if(lis.is_open()){
    while(lis.good()){
      //lis.getline(fname, 100, '\n');
      lis >> ff;
      if(lis.eof())break;
      std::cout << ff << std::endl;
      std::ifstream ifs(ff.c_str(), std::ifstream::in);
      char aux[2000000];
      int ctr = 0;
      if(ifs.is_open()){
	while(ifs.good()){
	  if(ifs.eof())break;
	  ifs.getline(aux, 2000000, '\n');
	  std::string s(aux);
	  std::string saux;
	  double amp, time;
	  //std::cout << "it:  " << ctr << " s: " << s << std::endl;
	  if(s.find("CH") ==  std::string::npos){
	    int length = s.size();
	    std::cout << "============Length: " << length<< std::endl;
	    int np1 = s.find("[[")+2;
	    int np2 = s.find("],");
	    std::cout << "debug 0" << std::endl;
	    saux = s.substr(np1, np2-np1);
	    time  = atof(saux.substr(0,saux.find(",")).c_str());
	    amp = atof(saux.substr(saux.find(",")+2, saux.size()-(saux.find(",")+2)).c_str());
	    if(ctr == 1){
	      Amp->push_back(amp);
	      Time->push_back(time);
	    }else if(ctr == 3){
	      Amp2->push_back(amp);
	      Time2->push_back(time);
	    }
	    //std::cout << ctr << " subs: " << saux << " " << time << " " << amp << std::endl;
	    np2 +=3;
	    s = s.substr(np2,length-np2);
	    while(np2 < length-1){
	      //std::cout << "debug 1" << std::endl;
	      np1 = s.find("[")+1;
	      np2 = s.find("],");
	      if(np2 == std::string::npos){
		//std::cout << "debug 2" << std::endl;
		np2 = s.find("]]");
		saux = s.substr(np1, np2-np1);
		time  = atof(saux.substr(0,saux.find(",")).c_str());
		amp = atof(saux.substr(saux.find(",")+2, saux.size()-(saux.find(",")+2)).c_str());
		//std::cout << ctr << " subs: " << saux << " " << time << " " << amp << std::endl;
		if(ctr == 1){
		  Amp->push_back(amp);
		  Time->push_back(time);
		}else if(ctr == 3){
		  Amp2->push_back(amp);
		  Time2->push_back(time);
		}
		break;
	      }else{
		//std::cout << "debug 2" << std::endl;
		//std::cout << "np1: " << np1 << " np2: " << np2 << std::endl;
		//std::cout << "string: " << s << std::endl;
		
		saux = s.substr(np1, np2-np1);
		//std::cout << "debug 2.1" << std::endl;
		time  = atof(saux.substr(0,saux.find(",")).c_str());
		//std::cout << "debug 2.2" << std::endl;
		amp = atof(saux.substr(saux.find(",")+2, saux.size()-(saux.find(",")+2)).c_str());
		//std::cout << "debug 2.3" << std::endl;
		if(ctr == 1){
		  Amp->push_back(amp);
		  Time->push_back(time);
		}else if(ctr == 3){
		  Amp2->push_back(amp);
		  Time2->push_back(time);
		}
	      }
	      np2 += 3;
	      s = s.substr(np2,length-np2);
	    }
	  }
	  ctr++;
	}
	
      }else{
	std::cout << "unable to open the file1" << std::endl;
      }
      
      t->Fill();
      std::cout << "bang!" << std::endl;
      Amp->erase(Amp->begin(), Amp->end());
      Amp2->erase(Amp2->begin(), Amp2->end());
      Time->erase(Time->begin(), Time->end());
      Time2->erase(Time2->begin(), Time2->end());
      ifs.close();
      evt++;
    }
  }else{
    std::cout << "Unable to open the File2" << std::endl;
  }

  std::cout << "Here!" << std::endl;
  //lis.close();
  
  TFile* f = new TFile("test_MPC_Dual.root", "RECREATE");
  t->Write();
  f->Close();
  
  return 0;
  
}
