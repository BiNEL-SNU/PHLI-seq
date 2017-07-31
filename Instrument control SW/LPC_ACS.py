"""
Created on Mar 13 2014
By Sungsik Kim, Seoul National University, Soeul, Korea
ACS Motorized stage operating module for PHLI-seq instrument at Biophotonics and Nanoengineering Lab. in SNU
"""

from acspy import acsc
import time

class ACS:
    """
    Methods:
    initialization
    move
    setVelocity
    getVelocity
    close
    """
    def __init__(self):
        self.hc=None
        self.initialization()

    def initialization(self):
        
        
        print "Waiting for Motorized Stage (ACS) Initialization"
        self.hc=acsc.openCommEthernetTCP(address="10.0.0.100", port=701)     ## craete comminucation

        acsc.runBuffer(self.hc,0)
        acsc.runBuffer(self.hc,1)
        acsc.runBuffer(self.hc,2)
        acsc.runBuffer(self.hc,4)
        acsc.runBuffer(self.hc,5)
        acsc.runBuffer(self.hc,6)

        time.sleep(30)

        
        ## Homing process


        ## Axis 6
        acsc.waitMotionEnd(self.hc, axis=6)         ## stop at left limit
        if acsc.setFPosition(self.hc, axis=6, fposition=0) != 0:
            print 'Axis 6 (Receiver Z): Homing completed'
        else:
            print 'Axis 6 (Receiver Z): Homing failed'
        

        ## Axis 0
        acsc.waitMotionEnd(self.hc, axis=0)
        acsc.toPoint(self.hc,flags=acsc.AMF_RELATIVE,axis=0,target=47.5)
        acsc.waitMotionEnd(self.hc, axis=0)
        if acsc.setFPosition(self.hc, axis=0, fposition=0) ==1:
            print 'Axis 0 (Sample X): Homing completed'
        else:
            print 'Axis 0 (Sample X): Homing failed'

        ## Axis 1
        acsc.waitMotionEnd(self.hc, axis=1)
        acsc.toPoint(self.hc,flags=acsc.AMF_RELATIVE,axis=1,target=19.51)
        acsc.waitMotionEnd(self.hc, axis=1)
        if acsc.setFPosition(self.hc, axis=1, fposition=0) ==1:
            print 'Axis 1 (Sample Y): Homing completed'
        else:
            print 'Axis 1 (Sample Y): Homing failed' 

        ## Axis 2
        acsc.waitMotionEnd(self.hc, axis=2)         ## stop at left limit
        acsc.toPoint(self.hc,flags=0,axis=2,target=2.8915)
        print 'Axis 2 (Lens array): Homing completed'

        ## Axis 4
        acsc.waitMotionEnd(self.hc, axis=4)         ## stop at left limit
        acsc.toPoint(self.hc,flags=acsc.AMF_RELATIVE,axis=4,target=4.42)
        acsc.waitMotionEnd(self.hc, axis=4)
        if acsc.setFPosition(self.hc, axis=4, fposition=0) ==1:
            print 'Axis 4 (Receiver X): Homing completed'
        else:
            print 'Axis 4 (Receiver X): Homing failed' 

        ## Axis5
        acsc.waitMotionEnd(self.hc, axis=5)         ## stop at left limit
        acsc.toPoint(self.hc,flags=acsc.AMF_RELATIVE,axis=5,target=23.8)
        acsc.waitMotionEnd(self.hc, axis=5)
        if acsc.setFPosition(self.hc, axis=5, fposition=0) ==1:
            print 'Axis 5 (Receiver Y): Homing completed'
        else:
            print 'Axis 5 (Receiver Y): Homing failed'


        
        
        ## parameter setting 
        acsc.setVelocity(self.hc,0,30)              ## axis 0 (linear X)
        acsc.setAcceleration(self.hc, 0, 100)
        acsc.setDeceleration(self.hc, 0, 100)
        acsc.setJerk(self.hc,0,1000)

        acsc.setVelocity(self.hc,1,30)               ## axis1 (linear Y)
        acsc.setAcceleration(self.hc, 1, 100)

        acsc.setDeceleration(self.hc, 1, 100)
        acsc.setJerk(self.hc, 1,1000)

        acsc.setVelocity(self.hc,2,30)              ## axis 2 (revolver)
        acsc.setAcceleration(self.hc, 2, 100)
        acsc.setDeceleration(self.hc, 2, 100)
        acsc.setJerk(self.hc,2,1000)

        acsc.setVelocity(self.hc,4,30)               ## axis4 (step X)
        acsc.setAcceleration(self.hc, 4, 100)
        acsc.setDeceleration(self.hc, 4, 100)
        acsc.setJerk(self.hc, 4,1000)

        acsc.setVelocity(self.hc,5,30)              ## axis 5 (step Y)
        acsc.setAcceleration(self.hc, 5, 100)
        acsc.setDeceleration(self.hc, 5, 100)
        acsc.setJerk(self.hc,5,1000)

        acsc.setVelocity(self.hc,6,5)               ## axis 6 (step Z)
        acsc.setAcceleration(self.hc, 6, 50)
        acsc.setDeceleration(self.hc, 6, 50)
        acsc.setJerk(self.hc, 1,100)

    def move(self, axis, distance, relative_or_absolute='r'):
        """
        'r' for relative, 'a' for absolute
        distance in [mm]
        """
        if relative_or_absolute == 'r':
            flags=acsc.AMF_RELATIVE
        else:
            flags=0
        acsc.getLastError()
        if not acsc.toPoint(self.hc, flags, axis, float(distance)):
            print "Transaction error: %d\n"% (acsc.getLastError())
        #acsc.waitMotionEnd(self.hc, axis=axis)

    def close(self):
        acsc.closeComm(self.hc)

    def setVelocity(self,axis,value):
        if not acsc.setVelocity(self.hc,axis,value):
            print "Transaction error: %d\n"% (acsc.getLastError())

    def getVelocity(self,axis):
        return acsc.getVelocity(self.hc,axis)

    def waitMotionEnd(self,axis,timeout=10000):
        return acs.acsc_WaitMotionEnd(self.hc, axis,timeout)

    def getPosition(self):
        return (acsc.getRPosition(self.hc,0),acsc.getRPosition(self.hc,1))


    ## modified @ 2015.2.24 by Sungsik Kim
    def getPosition_all(self):
        return (acsc.getRPosition(self.hc,0),acsc.getRPosition(self.hc,1),acsc.getRPosition(self.hc,2),acsc.getRPosition(self.hc,4),acsc.getRPosition(self.hc,5),acsc.getRPosition(self.hc,6))

    def getPosition2(self):
        return (acsc.getRPosition(self.hc,4),acsc.getRPosition(self.hc,5),acsc.getRPosition(self.hc,6))
    def MotionEnd(self):
        acsc.waitMotionEnd(self.hc, axis=0);
        acsc.waitMotionEnd(self.hc, axis=1);
        acsc.waitMotionEnd(self.hc, axis=2);
        acsc.waitMotionEnd(self.hc, axis=4);
        acsc.waitMotionEnd(self.hc, axis=5);
        acsc.waitMotionEnd(self.hc, axis=6);
        return 0;
    

            
            
