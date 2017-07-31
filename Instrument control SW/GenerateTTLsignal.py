# coding= latin-1

from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *
import numpy as np
import time

class GenerateTTLsignal():
    
    def __init__(self,DigitalOutputChannel):
        self.sampsPerChanWritten=c_int32()
        self.reserved=None
        self.data_0=np.ndarray(shape=(1,1),dtype=np.uint8,buffer=np.array([0]))
        self.data_1=np.ndarray(shape=(1,1),dtype=np.uint8,buffer=np.array([1]))

        DAQmxResetDevice(DigitalOutputChannel.split('/')[0])
        self.taskHandle = TaskHandle(0)
        DAQmxCreateTask("",byref(self.taskHandle))
        DAQmxCreateDOChan(self.taskHandle, DigitalOutputChannel, "", DAQmx_Val_ChanPerLine)
        DAQmxWriteDigitalLines (self.taskHandle,1,True,1, DAQmx_Val_GroupByScanNumber, self.data_0, byref(self.sampsPerChanWritten),cast(self.reserved,POINTER(c_ulong)))

    def TTL(self):
        DAQmxWriteDigitalLines (self.taskHandle,1,True,1, DAQmx_Val_GroupByScanNumber, self.data_1, byref(self.sampsPerChanWritten),cast(self.reserved,POINTER(c_ulong)))
        time.sleep(0.01)
        DAQmxWriteDigitalLines (self.taskHandle,1,True,1, DAQmx_Val_GroupByScanNumber, self.data_0, byref(self.sampsPerChanWritten),cast(self.reserved,POINTER(c_ulong)))
    
    def __del__(self):
        DAQmxClearTask(self.taskHandle)
    

if __name__=="__main__":
    laser=GenerateTTLsignal("Dev1/port0/line1")
