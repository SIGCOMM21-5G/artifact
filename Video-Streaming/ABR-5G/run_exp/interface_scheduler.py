import os
import sys
import time
from multiprocessing.connection import Listener
import threading

trace_file=sys.argv[1]
# algorithm=sys.argv[2]
interval=1.0
mode = 0
fiveg_throughputs = []
fourg_throughputs = []

with open(trace_file, 'r') as f:
    lines = f.readlines()
    for line in lines:
        parse = line.split('\t')
        fiveg = float(parse[1])
        fourg = float(parse[2][:-1])
        fiveg_throughputs.append(fiveg)
        fourg_throughputs.append(fourg)

startup_time = time.time()

def multipath_listener():
    global mode
    address = ('localhost', 9877)     # family is deduced to be 'AF_INET'
    listener = Listener(address, authkey='secret password')
    # print 'start listener'
    conn = listener.accept()
    # print 'connection accepted from', listener.last_accepted
    while True:
        msg = conn.recv()
        print(str(time.time()) + " recv msg: " + msg)
        if msg == 'enable':
            # switching overhead
            time.sleep(1.45)
            # enable 4G interface
            mode = 1
            idx = int(time.time()-startup_time)
            bw = int(fourg_throughputs[idx])
            if bw == 0:
                bw += 1
            os.system("sudo tc qdisc change dev ifb0 handle 1: root tbf rate "+str(bw)+"mbit burst 20k latency 58ms")
            print("%d 4G %4d Mbps" % (time.time(), bw))
        elif msg == 'close':
            conn.close()
            break
        elif msg =='disable':
            # switching overhead
            time.sleep(1.45)
            # disable 4G interface
            mode = 0
            idx = int(time.time()-startup_time)
            bw = int(fiveg_throughputs[idx])
            if bw == 0:
                bw += 1
            os.system("sudo tc qdisc change dev ifb0 handle 1: root tbf rate "+str(bw)+"mbit burst 20k latency 54ms")
            print("%d 5G %4d Mbps" % (time.time(), bw))
    listener.close()

def trace_replay():
    global mode
    # print the start timestamp
    print(time.time())
    idx = int(time.time()-startup_time)
    while idx < len(fiveg_throughputs):
        if mode == 1:
            # 4G
            bw = int(fourg_throughputs[idx])
        else:
            # 5G
            bw = int(fiveg_throughputs[idx])
        # tc command 
        if bw == 0:
            bw += 1
        os.system("sudo tc qdisc change dev ifb0 handle 1: root tbf rate "+str(bw)+"mbit burst 20k latency 54ms")
        if mode == 1:
            print("%d 4G: %4d Mbps" % (time.time(), bw))
        elif mode == 0:
            print("%d 5G: %4d Mbps" % (time.time(), bw))
        time.sleep(1)
        idx = int(time.time()-startup_time)
    
def main():
    t = threading.Thread(target=multipath_listener)
    t.start()
    trace_replay()


if __name__ == "__main__":
    main()
