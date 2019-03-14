import time



def f1(numRep):
    stt = time.time()
    for ii in range(numRep):
        time.sleep(0.01)
    return(time.time() - stt)
