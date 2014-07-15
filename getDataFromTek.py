#!/usr/bin/python arch -i386 python
#
# Date:   15-Jul-13
# Author:  Javier Duarte <jduarte@caltech.edu>
# Author: Cristian Pena <cristian.pena@caltech.edu>
# Author: Artur Apresyan <Artur.Apresyan@cern.ch>
import visa
import json, os
import time
import datetime
import filecmp
import sys
import ROOT as rt
from array import *

if __name__ == '__main__':
    
    index = 0
    current_data_fname = ""
    rt.gROOT.ProcessLine("struct MyStruct{Double_t ptime;};")
    from ROOT import MyStruct
    s = rt.MyStruct()

    tek = visa.instrument("USB0::0x0699::0x040C::C010783::INSTR", timeout=20, chunk_size=1024000) 
    while index < 10000000:
        # 200 MHz scope
        #tek = visa.instrument("USB0::0x0699::0x036A::C034250::INSTR")
        # 1 GHz scope
        #tek = visa.instrument("USB0::0x0699::0x040C::C010783::INSTR")
        #tek.chunk_size = 102400
        
        #instruments = visa.get_instruments_list()
        #usb = filter(lambda x: 'USB' in x, instruments)
        #if len(usb) != 1:
        #    print 'Bad instrument list', instruments
        #    sys.exit(-1)
        #tek = visa.instrument("USB0::0x0699::0x040C::C010783::INSTR", timeout=20, chunk_size=1024000) 
        # bigger timeout for long mem        
        print tek.ask("*IDN?")
        tek.write("DATA:SOURCE CH1")
        tek.write("DATA:ENCDG ASCII")
        tek.write("DATA:WIDTH 2")
        tek.write("DATA:START 1")
        #tek.write("DATA:STOP 2500")
        tek.write("DATA:STOP 10000")
        tek.write("WFMPRE?")
        ch1pre = tek.read()
        print "preamble:", ch1pre
        #tek.write("WFMPRE:PT_OFF?")
        tek.write("WFMO:PT_OFF?")
        ptoff = float(tek.read())
        #tek.write("WFMPRE:XZERO?")
        tek.write("WFMO:XZERO?")
        xzero = float(tek.read())
        #tek.write("WFMPRE:XINCR?")
        tek.write("WFMO:XINCR?")
        xincr = float(tek.read())
        #tek.write("WFMPRE:YOFF?")
        tek.write("WFMO:YOFF?")
        yoff = float(tek.read())
        #tek.write("WFMPRE:YMULT?")
        tek.write("WFMO:YMULT?")
        ymult = float(tek.read())
        #tek.write("WFMPRE:YZERO?")
        tek.write("WFMO:YZERO?")
        yzero = float(tek.read())
        print "x left = ", xzero
        #print "x right = ", xzero + xincr * (2500 - ptoff)
        print "x right = ", xzero + xincr * (10000 - ptoff)
        print "xincr = ", xincr
    
        tek.write("CURVE?")
        curve = tek.read()
        
        wave_y = [yzero + ymult * ( int(w) - yoff) for w in curve.split(",")]
        #wave_x = [xzero + xincr * ( n - ptoff) for n in range(0,2500)]
        wave_x = [xzero + xincr * ( n - ptoff) for n in range(0,10000)]

        ###############################################
        ################Mushing Data Around############
        ###############################################
        Amp = rt.std.vector( float )()
        Time = rt.std.vector( float )()
        minpeak = 100
        #for l in range(1,2500):
        for l in range(1,10000):
            if wave_y[l] < minpeak:
                minpeak = wave_y[l]
                
        print "====Signal Peak Found at: ", minpeak
        print "len(wave_y) = ", len(wave_y)
        wave = zip(wave_x,wave_y)
        
        s.ptime = time.time()#posix time in (maybe in sec)
        tstamp = datetime.datetime.fromtimestamp(s.ptime).strftime('%Y-%m-%d-%H_%M_%S')
        
        filename = "data_"+tstamp+".txt"
        rfile = "data_"+tstamp+".root"
        pdffile = "data_"+tstamp+".pdf"

        with open(filename,'w') as outfile:
            json.dump(wave, outfile)
        
        print "======FILENAME: ", filename   
        print "======CURRENT FILE: ", current_data_fname
        if current_data_fname == "":
            current_data_fname = filename

        flag = filecmp.cmp(current_data_fname,filename)
        print "FLAG: ", flag
        
        if flag == True and index != 0:
            command = "del "+filename
            os.system(command)
            print "deleting ", command
        elif flag == False and minpeak < -1.0:
            current_data_fname = filename
            ########################################
            ############## Writing to ROOT file ####
            ########################################
            with open(filename,'r') as infile:
                wave =  json.load(infile)
            wave_x, wave_y = zip(*wave)

            dx = wave_x[1]-wave_x[0]
            print wave_x[0]
            print dx
            
            tfile = rt.TFile(rfile,"RECREATE") 
            tree = rt.TTree("outTree", "outTree")
            tree.Branch("ptime", rt.AddressOf(s,'ptime'),"ptime/D")
            tree.Branch("Amp", Amp)
            tree.Branch("Time", Time)
            #histo1 = rt.TH1D("wave1","wave1",2500, wave_x[0], wave_x[-1]+dx)
            histo1 = rt.TH1D("wave1","wave1",10000, wave_x[0], wave_x[-1]+dx)
            for i in range(1,histo1.GetNbinsX()):
                Amp.push_back(wave_y[i-1])
                Time.push_back(wave_x[i-1])
                histo1.SetBinContent(i,wave_y[i-1])
    
            c = rt.TCanvas("c","c",500,500)
            histo1.SetTitle("")
            histo1.SetStats(0)
            
            histo1.GetYaxis().SetTitle("Volts")
            histo1.GetYaxis().CenterTitle()
            histo1.GetXaxis().SetTitle("seconds")
            histo1.GetXaxis().CenterTitle()
            histo1.Draw("")
    
            #c.Print(pdffile)
            tree.Fill()
            tree.Write()
            tfile.Close()
        elif minpeak >= -2.0 and index != 0:
            command = "del "+filename
            os.system(command)
            print "deleting ", command
        #os.system("python plot_v1.py")
        Amp.erase(Amp.begin(),Amp.end())
        Time.erase(Time.begin(), Time.end())
        print "++++++Vector Size+++++", Amp.size(), " ", Time.size
        time.sleep(1)
        index += 1
    
