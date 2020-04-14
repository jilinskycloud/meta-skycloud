import subprocess
import json
import os
import os.path
import sqlite3
from os import path
import base64
from Crypto.Cipher import AES
import redis
import time


r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)

global Xcount
Xcount = 0

class AutoConf:
  def __init__(self):
    print("This is the class...")
    '''
    f1  = "/tmp/flask_daemon.log"
    f2  = "/tmp/hb_daemon.log"
    f3  = "/tmp/http_daemon.log"
    f4  = "/tmp/autoC_daemon.log"
    f5  = "/tmp/logs_daemon.log"
    self.genFile(f1)
    self.genFile(f2)
    self.genFile(f3)
    self.genFile(f4)
    self.genFile(f5)
    '''
  '''  
  def genFile(self, path):
    print("cleating Files")
    try:
      str = "rm "+path
      os.system(str)
      #open(path, 'x')
    except FileExistsError:
      pass
  '''
  
  def read_file(self, path_):
    file_p = "/mnt/config_t.text"
    if path.exists(file_p) == True:
      with open(file_p,'r') as data:
        dd = data.read()
        return dd
    else:
      return 'null'

  def format_data(self, data):
    dd = data.split(',')
    print(dd)
    nonce = base64.b64decode(dd[0])
    ciphertext = base64.b64decode(dd[1])
    mac = base64.b64decode(dd[2])
    key = base64.b64decode(dd[3])
    print("Data Formate Function...")
    print(key)
    print(ciphertext)
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    #cipher = AES.new(key, AES.MODE_CCM, nonce)
    plaintext = cipher.decrypt(ciphertext)
    print(plaintext)
    plaintext = plaintext.decode("utf-8")
    plaintext = plaintext.split("~")
    data = {
      "enable_post_data": plaintext[0],
      "cache_size": plaintext[1],
      "gw_pass": plaintext[2],
      "heart_beat": plaintext[3],
      "server_socket": plaintext[4],
      "data_interval": plaintext[5],
      "serial_no": plaintext[6],
      "gw_uname": plaintext[7],
      "rssi_range": plaintext[8],
      "sniffer_type": plaintext[9],
      "protoc": plaintext[10]
    }
    try:
      cipher.verify(mac)
      with open("/www/web/_netw/conf/ble_conf.text", "w") as f:
        json.dump(data, f, indent=4)
        return data
    except ValueError:
      print("Key incorrect or message corrupted")

  def insert_sqlite(self, data):
    os.system("rm /www/web/gw_FlaskDb.db")
    conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
    conn.execute('CREATE TABLE login (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
    print("Table created successfully");
    # Insert Data to Login table
    print("UNAME::  ",data['gw_uname'])
    print("PASS:: ", data['gw_pass'])
    conn.execute("INSERT INTO login (username,password) VALUES (?,?)",(data['gw_uname'], data['gw_pass']) )
    conn.commit()
    msg = "Record successfully added"

  def re_write(self, data1):
    print("update Usb data...")
    dd = data1.split(',')
    print(dd)
    nonce = base64.b64decode(dd[0])
    ciphertext = base64.b64decode(dd[1])
    mac = base64.b64decode(dd[2])
    key = base64.b64decode(dd[3])
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    #cipher = AES.new(key, AES.MODE_CCM, nonce)
    plaintext = cipher.decrypt(ciphertext)
    print(plaintext)
    plaintext = plaintext.decode("utf-8")
    plt = plaintext.split("~")
    #print("--------------------------",plt[6])
    srl = plt[6]
    srl = srl.split("-")
    srl[1] = str(int( srl[1]) + 1).zfill(5)
    plt[6] = srl[0]+"-"+srl[1]
    print(plt[6])
    re_data = plt[0]+"~"+plt[1]+"~"+plt[2]+"~"+plt[3]+"~"+plt[4]+"~"+plt[5]+"~"+plt[6]+"~"+plt[7]+"~"+plt[8]+"~"+plt[9]+"~"+plt[10]
    re_data = str.encode(re_data)
    cipher12 = AES.new(key, AES.MODE_EAX)
    re_data = self.bs64(cipher12.nonce),self.bs64(cipher12.encrypt(re_data)),self.bs64(cipher12.digest()),self.bs64(key)
    return re_data

  def get_key(self, data):
    dd = data.split(',')
    key = dd[3]
    return key

  def bs64(self, vl):
    return str(base64.b64encode(vl), 'utf-8')

  def read_usb(self):
    path1 = "/dev/sda"
    for i in range(3):
      path_ = path1+str(i) 
      mm = path.exists(path_)
      print("this is the available USB path", mm)
      if mm == True:
        os.system("mount "+path_ +" /mnt/")
        data1 = self.read_file(path_)
        if data1 != 'null':
          data = self.format_data(data1)
          print("Lets do Configuration!!!!!!")
          print(data)
          self.insert_sqlite(data)   
          print("thi is done really")
          re_data = self.re_write(data1)
          with open("/mnt/config_t.text",'w') as f:
            f.write(str(re_data))
          key_ = self.get_key(data1)
          d1 = {
            "auto_config" : "yes",
            "key" :  key_
          }
          with open("/www/web/_autoConfig/config.txt",'w') as jsonfile:                    
            json.dump(d1, jsonfile, indent=4)                               
          print(d1) 
          os.system("umount "+path_)
          return 1
        else:
          print("File not exist!!!!")
    return 0

def main():
  d1 = json.load(open('/www/web/_autoConfig/config.txt','r'))
  print(d1['auto_config'])
  obj = AutoConf()
  if d1['auto_config']  == 'no':
    print("Going to config the GateWay...")
    r.mset({"blink-green": "0.2|green66|20|autoConf|check"})
    print(r.mget("blink-green"))
    obj.read_usb() 
  elif d1['auto_config'] == 'yes':
    print("GateWay Already Configured!")
    r.mset({"blink-green": "0.009|green66|40|autoConf|check"})

##MAIN FUNCTION
if __name__ == '__main__':
  while True:
    if os.path.exists("/var/run/ProcLevel.pid") == True:
      f = open("/var/run/ProcLevel.pid","r")
      pNo = f.read()
      f.close()
      #print(pNo)
      while pNo == "1":
        main()
        pNo = "2"
        f= open("/var/run/ProcLevel.pid","w+")
        f.write(pNo)
        f.close()
        time.sleep(2)	
    break

