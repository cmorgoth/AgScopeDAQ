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

    ag = visa.instrument("USB0::0x0957::0x900D::MY51050112::INSTR", timeout=20, chunk_size=1024000) 
    while index < 1000000000:
        #print ag.ask("*IDN?")
        ag.write(":WAVeform:SOURce CHANnel1")
        ag.write(":WAVeform:FORMat ASCII")
        ag.write(":WAVeform:POINts:MODE NORMal")
        ag.write(":WAVeform:POINts 100")
        
        #print ag.ask(":WAVeform:PREamble?")
        npoints  = int(ag.ask(":WAVeform:POINts?"))
        xref  = float(ag.ask(":WAVeform:XREFerence?"))
        xincr = float(ag.ask(":WAVeform:XINCrement?"))
        xorig = float(ag.ask(":WAVeform:XOrigin?"))
        yref  = float(ag.ask(":WAVeform:YREFerence?"))
        yincr = float(ag.ask(":WAVeform:YINCrement?"))
        yorig = float(ag.ask(":WAVeform:YORigin?"))
        #print "npoints = ", npoints
        #print "x origin = ", xorig
        #print "x increment = ", xincr
        #print "y origin = ", yorig
        #print "y increment = ", yincr
          
        curve = ag.ask("WAVeform:DATA?")
    
        curvelist = curve.split(",")[:-1]
        
        wave_y = [ float(w) for w in curvelist]
        wave_x = [xorig + xincr * ( n - xref)     for n in range(0,npoints-1)]
        
        ##############################################
        ####################CH2#######################
        ##############################################
            
        ag.write(":WAVeform:SOURce CHANnel3")
        ag.write(":WAVeform:FORMat ASCII")
        ag.write(":WAVeform:POINts:MODE NORMal")
        ag.write(":WAVeform:POINts 100")
        
        #print ag.ask(":WAVeform:PREamble?")
        npoints2  = int(ag.ask(":WAVeform:POINts?"))
        xref2  = float(ag.ask(":WAVeform:XREFerence?"))
        xincr2 = float(ag.ask(":WAVeform:XINCrement?"))
        xorig2 = float(ag.ask(":WAVeform:XOrigin?"))
        yref2 = float(ag.ask(":WAVeform:YREFerence?"))
        yincr2 = float(ag.ask(":WAVeform:YINCrement?"))
        yorig2 = float(ag.ask(":WAVeform:YORigin?"))
        #print "npoints = ", npoints2
        #print "x origin = ", xorig2
        #print "x increment = ", xincr2
        #print "y origin = ", yorig2
        #print "y increment = ", yincr2
          
        curve2 = ag.ask("WAVeform:DATA?")
        curvelist2 = curve2.split(",")[:-1]
        wave_y2 = [ float(w2) for w2 in curvelist2]
        wave_x2 = [xorig2 + xincr2 * ( n2 - xref2)     for n2 in range(0,npoints2-1)]

        ###############################################
        ################Mushing Data Around############
        ###############################################
        minpeak = 0.0
        for l in range(0,npoints-1):
            if wave_y2[l] < minpeak:
                minpeak = wave_y2[l]
                
        #print "====Signal Peak Found at: ", minpeak
        #print "len(wave_y) = ", len(wave_y)
        wave = zip(wave_x,wave_y)
        wave2 = zip(wave_x2,wave_y2)
        s.ptime = time.time()#posix time in (maybe in sec)
        #print "POSIX TIME: ", s.ptime
        #tstamp = datetime.datetime.fromtimestamp(s.ptime).strftime('%Y-%m-%d-%H_%M_%S')
        tstamp = int(round(time.time() * 1000))
        #print "Time Stamp: ", tstamp
        
        #filename = "data_"+tstamp+".txt"
        filename = "data_"+str(tstamp)+".txt"
        
        with open(filename,'w') as outfile:
            outfile.write('####CH1####\n')
            json.dump(wave, outfile)
            outfile.write('\n####CH2####\n')
            json.dump(wave2, outfile)
                    
        #print "======NEW FILE: ", filename   
        #print "======CURRENT FILE: ", current_data_fname
        if current_data_fname == "":
            current_data_fname = filename
            continue
        
        flag = filecmp.cmp(current_data_fname,filename)
        #print "FLAG: ", flag
        if flag == True:
            command = "del "+filename
            os.system(command)
            print "deleting ", command
        else:
            if minpeak < -0.078:
                current_data_fname = filename
            else:
                command = "del "+filename
                os.system(command)    
                print "deleting ", command
                
        time.sleep(.01)
        index += 1
    
