import httplib2
import time
import subprocess
import urllib
import json
import signal
import os
import redis
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64
import serial
r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)
r1 = redis.StrictRedis(host='localhost', port=6370, db=1, charset="utf-8", decode_responses=True)
http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)

global HB
global PRO
global sr_no
global d1
global Xcount 

Xcount = 0
HB = "OFF"
PRO = "OFF"
sr_no = "0000000"
d1 = None

def status_():
  global HB
  global PRO
  global sr_no
  global d1
  d1 = json.load(open('/www/web/_netw/conf/ble_conf.text','r'))
  sr_no = d1['serial_no']
  if d1['enable_post_data'] == 'on' and d1['protoc'] == 'HTTP':
    HB = "ON"
    PRO = 'HTTP'
    #print("i got on signal http")
  elif d1['enable_post_data'] == 'on' and d1['protoc'] == 'MQTT':
    #print("i got on signal mqtt")
    HB = "ON"
    PRO = 'MQTT'
    
  else:
    HB = "OFF"
    PRO = "OFF"
    #print("I got off signal or post data!")
  return HB

HB = status_()

def log(log_str):                                                                                                                  
    global Xcount                                                                                        
    #print("in log...........:: ",Xcount)
    log_str = str(log_str)+" \n"                                                                                                   
    Xcount = Xcount+1                                                                                                              
    if os.path.exists("/tmp/http_daemon.log") == False:                                                                                             
        #print("File not exist CEATING IT")                                                                                         
        open("/tmp/http_daemon.log", "w").close()                                                                                                   
    with open('/tmp/http_daemon.log', 'a') as outfile:                                                                                                  
        outfile.write(log_str)                                                                                                     
    if Xcount > 10000:                                                                                                                              
        os.system("rm /tmp/http_daemon.log")
        Xcount = 0                                                                        
    return  


def receive_signal(signum, stack):
  global HB
  log('Got Config File Changed Signal :: '+str(signum))
  #print("here im getting a signal and calling the sattus function to enable and disable the post data of ble")
  HB = status_()

signal.signal(signal.SIGUSR1, receive_signal)
pidis = str(os.getpid())
msg = 'My PID : '+str(pidis)
log(msg)


f= open("/var/run/ble_post.pid","w+")
f.write(pidis)
f.close()

def encrypt_http(out):
  log("----------ENCRYPT THE SENDING DATA----------")
  data = out 
  d1 = json.load(open('/www/web/_autoConfig/config.txt','r'))
  key = d1['key']
  key = base64.b64decode(key)
  cipher = AES.new(key, AES.MODE_EAX)
  ciphertext, tag = cipher.encrypt_and_digest(data)
  data = {'nonce':bs64(cipher.nonce), 'ciphertext':bs64(ciphertext), 'tag':bs64(tag)}
  return data 

#--------------------------------------------------------------------------------------------------
def bs64(vl):
  return str(base64.b64encode(vl), 'utf-8')

def encrypt(out):
  log("----------ENCRYPT THE SENDING DATA----------")
  data = out 
  d1 = json.load(open('/www/web/_autoConfig/config.txt','r'))
  key = d1['key']
  key = base64.b64decode(key)
  cipher = AES.new(key, AES.MODE_EAX)
  data = bs64(cipher.nonce),bs64(cipher.encrypt(data)),bs64(cipher.digest())
  return data 

#--------------------------------------------------------------------------------------------------
def data_split(data):
  global sr_no
  a = data
  mac = a[6:18]
  rssi = a[18:20]
  adv = a[20:38]
  uuid = a[38:70]
  maj = a[70:74]
  mina = a[74:78]
  tx = a[78:80]
  tx = int(tx, 16)- 256
  received = {'mac':mac, 'rssi':rssi, 'adv':adv, 'uuid':uuid, 'maj':maj, 'mina':mina, 'tx':tx}
  received = {'mac':mac, 'rssi':rssi, 'adv':adv, 'uuid':uuid, 'maj':maj, 'mina':mina, 'tx':tx, 'sr_no':sr_no} 
  return received

def verify_mac(v_mac):
    obj = r.scan_iter()
    blk_ble = r.lrange("white_listed", 0, -1)
    log(str(blk_ble))
    if v_mac in blk_ble:
    	log(str(v_mac))
    	return 1
    else:
    	log(str(v_mac))
    	return 0
def get_average(t_rssi):
	plus = 0
	for v in range(len(t_rssi)):
		plus  = plus + int(t_rssi[v])
		avg = plus/len(t_rssi)
	return avg
def insert_r1(data1, cache_lim):
    log("----------Insert RSSI into R1 Database For Average----------")
    x = int(data1['rssi'], 16)
    r1.lpush(data1['mac'], x)
    r1.ltrim(data1['mac'],0, cache_lim)
    t_rssi = r1.lrange(data1['mac'],0,-1)
    avg = get_average(t_rssi)
    return avg



def send():
	global HB
	global PRO
	global d1
	log("---------- Data Post Status is :: "+HB+" and Protocol is :: "+PRO+" ----------")
	# Open Serial Port !!!!!!!                             
	ser = serial.Serial('/dev/ttymxc2')                    
	ser.baudrate = 115200  
	ser.close()                                                                                   
	ser.open()                                            
	while(1):
		time.sleep(int(d1['data_interval']))
		if HB == "ON":                                                                                                                                       
			#print("Here i'm in post data loop its ON for send")
			out = 0
			data = ser.read(42).hex()
			out = data
			#print(out)
			if len(out) == 84:
				#print("post data is on and packet length is 84 now ready to send the packet")
				avg = 0
				#print(out)
				out1 = data_split(out)
				v_chk = verify_mac(out1['mac'])
				ble_rssi = int(out1['rssi'], 16) - 256
				rssi_lim = d1['rssi_range']
				rssi_lim = rssi_lim.split("|")
				cache_lim = d1['cache_size']
				if v_chk == 1 and ble_rssi < int(rssi_lim[0]) and ble_rssi > int(rssi_lim[1]):
					log("----------This MAC is White listed -- Ready to send----------")
					log(str(out1['mac']))
					avg = int(insert_r1(out1, int(cache_lim)))  #it returns avg value
					out1['rssi'] = avg - 256
					log("After RSSI Normalization "+str(out1))
					out1 = json.dumps(out1).encode('utf-8')
					log("out1 butes ::"+str(out1))
					log(str(out1))
					if PRO == 'HTTP':
						log("!!!!!----------------THIS IS THE HTTP -- Data Encrypted----------------!!!!!")
						body = encrypt_http(out1)
						#print("this is the read outpuut", out1)
						http_url = "http://"+d1['server_socket']+"/http_test"	      			
						try:
							content = http.request(http_url, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body))[1]
							r.mset({"blink-blue":"0.001|blue67|0|dataPost|check"})
						except Exception as e:
							r.mset({"blink-blue": "0|0|0|0|0"})
							#raise e
							pass
						log("---SENDING BY HTTP PROTOCOL---")
					elif PRO == 'MQTT':
						log("!!!!!----------------THIS IS THE MQTT -- Data Encrypted----------------!!!!!")
						data = encrypt(out1)
						a = json.dumps(data)
						add = d1['server_socket']
						add = add.split(":")
						ip =  add[0]
						add = "tcp://"+ip+":1883"   #'tcp://192.168.0.74:1883'
						cid = 'ExampleClientPub'
						tpc = 'exp'
						cmd = '/www/web/_netw/mqtt_post '+add+' '+cid+' '+tpc+' '+"'"+a+"'"
						proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)                                                      
						(out1, err1) = proc.communicate()
						r.mset({"blink-blue":"0.001|blue67|0|dataPost|check"})
						log("---SENDING BY MQTT PROTOCOL---")
					else:
						log("XXXXX -- Black listed MAC or RSSI is out of Range -- XXXXX")
				else:
					log("XXXXXX--DATA LENGTH ERROR!!!--XXXXXX")
		elif HB == "OFF":
			r.mset({"blink-blue": "0|0|0|0|0"})
			if os.path.exists("/var/run/ble_post.pid") == 'True':
				log(os.system("cat /var/run/ble_post.pid"))
				pi1 = open("/var/run/ble_post.pid", 'r')
				pid_1 = pi1.read()
				pi1.close()
				os.system('kill -s 10 ' + pid_1)

def main():
  send()

if __name__ == '__main__':
  while True:
    f = open("/var/run/ProcLevel.pid","r")
    pNo = f.read()
    f.close()
    if pNo == "4":
      pNo = "5"
      f= open("/var/run/ProcLevel.pid","w+")
      f.write(pNo)
      f.close()  
      main()






