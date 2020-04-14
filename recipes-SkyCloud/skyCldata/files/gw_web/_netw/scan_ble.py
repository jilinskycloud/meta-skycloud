import subprocess
import redis
import json
import os
import time
import serial

r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)
r1 = redis.StrictRedis(host='localhost', port=6370, db=1, charset="utf-8", decode_responses=True)


def data_split(data):
  a = data
  mac = a[6:18]
  rssi = a[18:20]
  rssi = int(rssi, 16) -256
  adv = a[20:38]
  uuid = a[38:70]
  maj = a[70:74]
  mina = a[74:78]
  tx = a[78:80]
  tx = int(tx, 16) -256
  received = {'mac':mac, 'rssi':rssi, 'adv':adv, 'uuid':uuid, 'maj':maj, 'mina':mina, 'tx':tx}
  return received

def verify_mac(v_mac):
    obj = r.scan_iter()
    blk_ble = r.lrange("white_listed", 0, -1)
    print(blk_ble)
    if v_mac in blk_ble:
      #r.rpush("white_listed", wht_mac)
      return 1
    else:
      return 0

def insert_r1(data1):
    print("This is R1 data insert Function!--------------------------------------------------------------------------00000000000000000000000000000000000000000000000000")
    print(data1)
    r1.hmset(data1['mac'], {'mac':data1['mac'], 'rssi':data1['rssi'], 'adv':data1['adv'], 'uuid':data1['uuid'], 'maj':data1['maj'], 'mina':data1['mina'], 'tx':data1['tx']})
    r1.expire(data1['mac'], 300)
    print(r1.hgetall(data1['mac']))




d1 = json.load(open('/www/web/_netw/conf/ble_conf.text','r'))
print(d1['enable_post_data'])
post_ble = d1['enable_post_data']

def kill_proc():
	print("Kill other ble process!")
	proc = subprocess.Popen(["ps ax | grep 'python3 /www/web/_netw/_httplib.py' | grep -v grep | awk '{print $1}'"], stdout=subprocess.PIPE, shell=True)
	(pid, err) = proc.communicate()
	pid = str(pid,'utf-8')
	#print("PID of Process is :: ", pid)
	cmd = "kill -9 " + str(pid)
	os.system(cmd)

def scan_it():
	a=1
	r.mset({"blink-blue":"0.1|blue67|0|scanBle|check"})
	# Open Serial Port !!!!!!!
	ser = serial.Serial('/dev/ttymxc2')
	ser.baudrate = 115200  
	ser.close()
	ser.open()             
	#!!!!!!!!!!!!!!!!!!!!!!!!!
	while(a != 80):
		data = ser.read(42).hex()
		print(data)
		if len(data) > 0:
			print("The data length is ", len(data))	
			print(type(data))
			if len(data) == 84:
				data1 = data_split(data)
				print("fkng RSSI----------------------------------------------------------",data1['rssi'])

				r.lpush("scanned", data1)
				r.expire("scanned", 400)

				print(r1.lrange(data1['mac'],0,-1))
				a=a+1
	ser.close()

def turn_post(stat):
	with open('/www/web/_netw/conf/ble_conf.text', 'r+') as f:
		data = json.load(f)
		data['enable_post_data'] = stat # <--- add `id` value.
		f.seek(0)        # <--- should reset file position to the beginning.
		json.dump(data, f, indent=4)
		f.truncate()


if post_ble == 'on':
	stat = 'off'
	turn_post(stat)
	kill_proc()	
	scan_it()
	stat = 'on'
	turn_post(stat)
	pNo = "4"
	f= open("/var/run/ProcLevel.pid","w+")
	f.write(pNo)                        
	f.close() 
	os.system("/etc/init.d/http_daemon start")
elif post_ble == 'off':
	kill_proc()
	scan_it()
	pNo = "4"
	f= open("/var/run/ProcLevel.pid","w+")
	f.write(pNo)
	f.close()
	os.system("/etc/init.d/http_daemon start")  
