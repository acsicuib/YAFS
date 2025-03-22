
import time

class myTime:

    def __init__(self, print_):
        self.myPreviousTime_ = time.time()
        self.print_ = print_

    
    
    def s(self):
        self.myPreviousTime_ = time.time()
        
    
    def c(self,s_='classtime'):
        
        
        
        now_ = time.time()
        if self.print_:
            print (s_ +" "+ str(now_ -self.myPreviousTime_))    
        self.myPreviousTime_ = now_
    

