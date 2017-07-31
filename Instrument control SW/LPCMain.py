"""
Created on Mar 13 2014
By Sungsik Kim, Seoul National University, Seoul, Korea
Interactive Console to control PHLI-seq instrument at Biophotonics and Nanoengineering Lab. in SNU.
"""
import LPC_ACS
import serial
import time

## function def
def FourAxisStop():
    while (True):
        time.sleep(0.2)
        FourAxis.write('SPD\r')
        FA=FourAxis.read(100)
        if FA=='SPD 00000000, 00000000, 00000000, 00000000\n\r':
            break

def LED_off():
    il_4ch.write('1STA\r\n')
    if il_4ch.read(100).split()[1]=='ON': il_4ch.write('1IOF\r\n')
    il_4ch.write('2STA\r\n')
    if il_4ch.read(100).split()[1]=='ON': il_4ch.write('2IOF\r\n')
    il_4ch.write('3STA\r\n')
    if il_4ch.read(100).split()[1]=='ON': il_4ch.write('3IOF\r\n')
    il_4ch.write('4STA\r\n')
    if il_4ch.read(100).split()[1]=='ON': il_4ch.write('4IOF\r\n')
            


## open comminiocation 
il_2ch =serial.Serial(port='COM3',baudrate=9600, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE,  timeout=0.1)        ## port depends on local PC environment
AF=serial.Serial(port='COM4',baudrate=9600, bytesize=7, stopbits=serial.STOPBITS_ONE,  timeout=0.1)        ## port depends on local PC environment
il_4ch =serial.Serial(port='COM6',baudrate=9600, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE,  timeout=0.1)        ## port depends on local PC environment
FourAxis = serial.Serial(port='COM5',baudrate=9600, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE,  timeout=0.1)        ## port depends on local PC environment
acs=LPC_ACS.ACS()                     ## ACS stage homing, Revceiver homing location should be determied (LPC_ACS.py)

FourAxis.write('HOM XYZU '+'\r')       ## Four axis motor homing
FourAxisStop()
FourAxis.write('PAB ,,183718'+'\r')
FourAxisStop()
print 'Slit & LED changer motors : Homing completed'




scriptFlag=False
      
    

while(True):
    try:
        if not scriptFlag:
            print "Command: ",
            cmd=raw_input()
        else:
            line=f.readline()
            if line.split()==[]:continue
            if line.split()==['EOF']:
                scriptFlag=False
                continue
            cmd=line[:-1]
            print cmd
            
            
        cmd=cmd.split()
        if cmd==[]:continue
        
        ## case1: sample stage
        if cmd[0]=='stage1': 
            """
            stage1 mv x 10
            stage1 mv 3 4
            stage1 setv x 10
            stage1 getv x
            """
            dict_xy={'x':0,'y':1,'z':2}
            if cmd[1]=='mv':
                if cmd[2] in dict_xy :
                    if cmd[2] != 'z':
                        acs.move(dict_xy[cmd[2]],cmd[3])
                    else:
                        AF.write('#MV %s\r\n'%(str(int(int(cmd[3])*12.72))))
                  
                else:
                    acs.move(0,cmd[2])
                    acs.move(1,cmd[3])
                acs.waitMotionEnd(0)
                acs.waitMotionEnd(1)
                    
            elif cmd[1]=='setv':
                acs.setVelocity(dict_xy[cmd[2]],cmd[3])
            elif cmd[1]=='getv':
                acs.move(cmd[2])
            else:
                print 'Error: Format Error'
                continue

##            

        ## case2: 96 plate stage
        elif cmd[0]=='stage2': ## 96 palte stage
            """
            stage2 mv x 10
            stage2 mv 3 4
            stage2 setv x 10
            stage2 getv x
            """
            dict_xy={'x':4,'y':5,'z':6}
            if cmd[1]=='mv':
                if cmd[2] in dict_xy : acs.move(dict_xy[cmd[2]],cmd[3])
                else:
                    acs.move(4,cmd[2])
                    acs.move(5,cmd[2])
            elif cmd[1]=='setv':
                acs.setVelocity(dict_xy[cmd[2]],cmd[3])
            elif cmd[1]=='getv':
                acs.move(cmd[2])
            else:
                print 'Error: Format Error'
                continue

        ## case3: lens array 
        elif cmd[0]== 'lens':
            """
            lens 1
            """
            dict_lens={'1': 2.8915 ,'2':40.9165, '3':78.9415, '4':116.9515, '5':154.9415}
            acs.move(2,dict_lens[cmd[1]], 'a')

        ## case4: Bright field (transmitted)
        elif cmd[0] == "bf":
            """
            bf on
            bf off
            bf [0-100]
            """
            if cmd[1] =='on':
                il_2ch.write('1ION\r\n')
            elif cmd[1] =='off':
                il_2ch.write('1IOF\r\n')
            else:
                try:
                    intensity = int(float(cmd[1])*5.11)
                    il_2ch.write('1BRT '+str(intensity)+'\r\n')
                except:
                    print 'Error: Format Error'
                    continue
                
        ## case 5: target illumination
        elif cmd[0] == "target":
            """
            target on
            target off
            target [0-100]
            """
            if cmd[1] =='on':
                il_2ch.write('2ION\r\n')
            elif cmd[1] =='off':
                il_2ch.write('2IOF\r\n')
            else:
                try:
                    intensity = int(5.11*float(cmd[1]))
                    il_2ch.write('2BRT '+str(intensity)+'\r\n')
                except:
                    print 'Error: Format Error'
                    continue

        ## case 6: fluorescence
        elif cmd[0] == "fluorescence":
            """
            fluorescence ch1 on
            fluorescence ch1 off
            fluorescence ch1 [0-100]
            ch1: UV ex, ch2: blue ex, ch3: green ex
            """
            cmd_=''     ## command for illumination control
            cmd_4A=''   ## command for LED changer
            if cmd[2] in ['on','off']: LED_off()
            if cmd[1]=='ch1':
                cmd_+='4'
                cmd_4A='PAB ,,183718'+'\r'
            elif cmd[1] =='ch2':
                cmd_+='3'
                cmd_4A='PAB ,,121718'+'\r'
            elif cmd[1] =='ch3':
                cmd_+='2'
                cmd_4A='PAB ,,58968,'+'\r'
            else :
                print 'Error: Format Error'
                continue
            
            if cmd[2] =='on':
                cmd_+='ION'
            elif cmd[2] =='off':
                cmd_+='IOF'

            else:
                try:
                    cmd_+= ('BRT '+str(int(2500+630.35*float(cmd[2]))))
                   
                except:
                    print 'Error: Format Error'
                    continue
            
            FourAxis.write(cmd_4A)
            FourAxisStop()
            il_4ch.write(cmd_+'\r\n')

        ## case 7: reflective bf
        elif cmd[0] == "rbf":
            """
            rbf on
            rbf off
            rbf [0-100]
            """
            if cmd[1] =='on':
                LED_off()
                FourAxis.write('PAB ,,183718'+'\r')
                FourAxisStop()
                il_4ch.write('1ION\r\n')
            elif cmd[1] =='off':
                LED_off()
            else:
                try:
                    intensity = int(2500+630.35*float(cmd[1]))
                    il_4ch.write('1BRT '+str(intensity)+'\r\n')
                except:
                    print 'Error: Format Error'
                    continue
            
        ## case 8: slit
        elif cmd[0] == 'slit':
            """
            slit x [-7 ~ 7]
            slit y [-7 ~ 7]
            slit t [-7 ~ 7]
            """
            if len(cmd) !=3:
                print 'Error: Format Error'
                continue
            
            if int(cmd[2])<0:
                pulse=-10*pow(3,-int(cmd[2]))
            else:
                pulse=10*pow(3,int(cmd[2]))
                
            if cmd[1]=='x':
                FourAxis.write('PIC '+str(pulse)+'\r')
            elif cmd[1]=='y':
                FourAxis.write('PIC ,'+str(pulse)+'\r')
            elif cmd[1]=='t':
                FourAxis.write('PIC ,,,'+str(pulse)+'\r')
            else: 
                print 'Error: Format Error'
                continue
        ## case 9: autofocusing
        elif cmd[0] == 'af':
            """
            af recipe [T/R] [1-5]
            af offset?
            af offset 160
            af
            """
            if len(cmd)==1:
                AF.write('#AF\r\n')
            elif cmd[1]=='recipe':
                if cmd[2]=='R':
                    d={'1':'A','2':'B','3':'C','4':'D','5':'E'}
                elif cmd[2]=='T':
                    d={'1':'F','2':'G','3':'H','4':'I','5':'J'}
                else:
                    print 'Error: Format Error'
                    continue
                print '#AF '+d[cmd[3]]
                AF.write('#AP '+d[cmd[3]]+'\r\n')
            elif cmd[1]=='offset?':
                AF.write('#RPGO\r\n')
                os= AF.read(100)
                os=os.split()[-1]
                print 'OFFSET %s'%(os)
            elif cmd[1]=='offset':
                if len(cmd) != 3:
                    print 'Error: Format Error'
                    break
                AF.write('#RPGO\r\n')
                os= AF.read(100)
                os=os.split()
                os[5]=cmd[2]
                AF.write(' '.join(os)+'\r\n')
            else:
                print 'Error: Format Error'
                continue

        elif cmd[0]=='pos_all':
            # (stage1_x, stage1_y, lens_pos, stage2_x, stage2_y, stage2_z)
            print acs.getPosition_all()

        elif cmd[0]=='AF_pos':
            AF.read(100)
            AF.write('#RP \r\n')
            z_abs_pos=float(AF.read(100).split()[1])/12.72
            print z_abs_pos
            


        elif cmd[0]=='q':
            break
        else:
            print 'Error: Format Error'
            continue
    except:
        print 'Error: Format Error'
        continue

###Dinsconnet communications
il_2ch.close()
AF.close()
il_4ch.close()
FourAxis.close()
acs.close()

#

