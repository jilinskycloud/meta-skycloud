import httplib2
import time
import json
import os
import signal
import urllib
import base64
import subprocess
import redis

r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)
global HB
global content
global server_socket
global serial_no
global Xcount
content = ""
Xcount = 0
HB = "OFF"
server_socket = "NULL"
serial_no = "NULL"

def log(log_str):                                                                                
    global Xcount                                                                                
    #print("in log...........:: ",Xcount)                                                         
    log_str = str(log_str)+" \n"                                                                 
    Xcount = Xcount+1                                                                            
    if os.path.exists("/tmp/hb_daemon.log") == False:                    
        #print("File not exist CEATING IT")                       
        open("/tmp/hb_daemon.log", "w").close()                   
    with open('/tmp/hb_daemon.log', 'a') as outfile:              
        outfile.write(log_str)                                   
    if Xcount > 100:                                           
        os.system("rm /tmp/hb_daemon.log")                        
        Xcount = 0                                               
    return   

def status_():
	global HB
	global server_socket
	global serial_no
	d1 = json.load(open('/www/web/_netw/conf/ble_conf.text','r'))
	d2 = json.load(open('/www/web/_netw/conf/wifi_conf.text','r'))
	server_socket = d1['server_socket']
	log("Server Socket :: "+server_socket)
	serial_no = d1['serial_no']
	if d1['heart_beat'] == 'on' or d2['w_heart_beat'] == 'on':
		HB = "ON"
		
	else:
		HB = "OFF"

	return HB

HB = status_()

def receive_signal(signum, stack):
	global HB
	HB = status_()

signal.signal(signal.SIGUSR1, receive_signal)
pidis = str(os.getpid())
log('My PID:'+pidis)
f= open("/var/run/heartbeat.pid","w+")
f.write(pidis)
f.close()

def redis_started():
	proc = subprocess.Popen(["redis-cli -p 6370 ping"], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	out = out.decode("utf-8")
	if out == "PONG\n":
		out = 1
	else:
		out = 0
	return out

def beat():
	while(1):
		time.sleep(1)
		global HB
		global content 
		_sr = serial_no.encode()
		_sr = base64.b64encode(_sr)   
		log("Heart Beat Status :: "+HB)
		body = {'sr':_sr}
		if HB == "ON":
			http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)
			url_ = "http://"+server_socket+"/heartBeat/"
			try:
			 	content = http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
			 	r.mset({"blink-green": "0.005|green66|0|heartbeat|check"})
			 	content = content.decode("utf-8")
			except Exception as e:
				r.mset({"blink-green": "0|0|0|0|0"})
				pass 
			log("[ Time :: "+time.ctime()+" ] | Server Response to Gateway :: "+content)
			if redis_started() == 1:
				if content == 'success':
					r.set("hbeat", 'connected')
					log("Redis Server is Connected!")
				else:
					log("Not Connected!")
					r.set("hbeat", 'disconnected')
		elif HB == 'OFF':
			r.mset({"blink-green": "0|0|0|0|0"})
			if redis_started() == 1:
				log("Server Not Connected!")
				r.set("hbeat", 'disconnected')
			else:
				log("Redis Not Connected !!!!!")


def main():
	while(1):
		beat()

##MAIN FUNCTION
if __name__ == '__main__':
	while True:
		if os.path.exists("/var/run/ProcLevel.pid") == True:
			f = open("/var/run/ProcLevel.pid","r")
			pNo = f.read()
			f.close()
			if pNo == "3":
				pNo = "4"
				f= open("/var/run/ProcLevel.pid","w+")
				f.write(pNo)
				f.close()
				while True:   
					main()
				break