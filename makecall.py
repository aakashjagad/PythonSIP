#This script register two endpoints and makes a call from endpoint 1 to endpoint 2.

import sys
import argparse
import threading
import pjsua as pj
import time
def logprint(level,str,len):
    with open('logfile.txt','r+') as file:
        file.write(str)

class MyAccountCallback(pj.AccountCallback):
    lock = None

    def __init__(self,account):
        pj.AccountCallback.__init__(self,account)

    def wait(self):
        self.lock = threading.Semaphore(0)
        self.lock.acquire()

    def on_reg_state(self):
        if self.lock:
            if self.account.info().reg_status >= 200:
                self.lock.release()
    def on_incoming_call(self,call):
        call.answer(200)


class MyCallCallback(pj.CallCallback):

    def __init__(self,call=None):
        pj.CallCallback.__init__(self,call)
    def on_state(self):
        print ("Call state: ",self.call.info().state_text,self.call.info().last_code,self.call.info().last_reason)
        if self.call.info().state == 6:
            print ("Answered Call Duration :",self.call.info().call_time)
            print ("Total Call Duration :",self.call.info().total_time) 
      

# Arguments for make call Endpoint1, password, Endpoint 2, password. 

parser = argparse.ArgumentParser()
parser.add_argument("Endpoint1", type=str, help ="Enter endpoint 1")
parser.add_argument("Endpt1pass", type=str, help ="Enter endpoint 1 password")
parser.add_argument("Endpoint2", type=str, help ="Enter endpoint 2")
parser.add_argument("Endpt2pass", type=str, help ="Enter endpoint 2 password")
args = parser.parse_args()

lib1 = pj.Lib()

lib1.init(log_cfg = pj.LogConfig(level=4,callback=logprint))
lib1.create_transport(pj.TransportType.UDP,pj.TransportConfig(5080))
lib1.set_null_snd_dev()
lib1.start()

end1 = lib1.create_account(pj.AccountConfig("phone.plivo.com",args.Endpoint1,args.Endpt1pass))
endcb1 = MyAccountCallback(end1)
end1.set_callback(endcb1)
endcb1.wait()

print ("\nRegistration Info "+(args.Endpoint1)+" state=", end1.info().reg_status,end1.info().reg_reason)

end2 = lib1.create_account(pj.AccountConfig("phone.plivo.com",args.Endpoint2,args.Endpt2pass))
endcb2 = MyAccountCallback(end2)
end2.set_callback(endcb2)
endcb2.wait()

print ("\nRegistration Info "+(args.Endpoint2)+" state=", end2.info().reg_status,end2.info().reg_reason)

sipuri = "sip:"+args.Endpoint2+"@phone.plivo.comi:5080"
current_call = end1.make_call(sipuri,cb=MyCallCallback())

time.sleep(15) 
current_call.hangup(600,"Call disconnected")
current_call.dump_status()
time.sleep(1)
end1.delete()
end2.delete()
lib1.destroy()












