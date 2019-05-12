#!/usr/bin/env python3
import argparse
import time
import datetime
import sys
import json
import subprocess
import os
import signal
import platform
import threading
import helper
from random import randint
import re
import random
import shutil
from flask import Flask, render_template,redirect


def getVersion():
   rt={}
   try:
     if "vsw-file" in GLB_configuration:
       with open(GLB_configuration["vsw-file"]) as json_data:
          rt=json.load(json_data)
   except Exception as e:
        helper.internalLogger.error('no vsw json data')
        helper.einternalLogger.exception(e)  
   return rt


from flask import Flask, jsonify,abort,make_response,request, url_for

from helper import *




'''----------------------------------------------------------'''
def getDirSize(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def getFreeDiskSize(path = '.'):
    rt = 0
    statvfs = os.statvfs(path)
    #statvfs.f_frsize * statvfs.f_blocks     # Size of filesystem in bytes
    #rt=statvfs.f_frsize * statvfs.f_bfree      # Actual number of free bytes
    rt=statvfs.f_frsize * statvfs.f_bavail     # Number of free bytes that ordinary users
    return rt




'''----------------------------------------------------------'''
'''----------------------------------------------------------'''

def format_datetime(value):
    aux="unknown"
    try:
      aux=time.ctime(value)
    except Exception as e:
      helper.internalLogger.critical("Error reading value date: {0}.".format(value))
      helper.einternalLogger.exception(e)
    return aux 

'''----------------------------------------------------------'''
'''----------------------------------------------------------'''

def format_videoURL(value):
    aux="unknown"
    try:
      aux=value[1:]
    except Exception as e:
      helper.internalLogger.critical("Error reading value date: {0}.".format(value))
      helper.einternalLogger.exception(e)
    return aux
'''----------------------------------------------------------'''
'''----------------      API REST         -------------------'''
'''----------------------------------------------------------'''
api = Flask("api",template_folder="templates",static_folder='static')
api.jinja_env.filters['datetime'] = format_datetime
api.jinja_env.filters['videoURL'] = format_videoURL




def getStatus():

    rt={}

    rt['disk']={'totalFree': 0,'projects':0,'ongoing':0}
    rt['disk']['projects']=getDirSize(GLB_configuration["mediaPath"])
    rt['disk']['totalFree']=getFreeDiskSize(GLB_configuration["mediaPath"])
 


    return rt
'''----------------------------------------------------------'''
@api.route('/',methods=["GET", "POST"])
def home():
    if request.method == 'POST':
      helper.internalLogger.debug("Processing new request from a form...{0}".format(request.form))
      form2 = request.form.to_dict()
      helper.internalLogger.debug("Processing new request from a form2...{0}".format(form2))   
      requestNewOngoing(form2)

    timelapse={}
 
    timelapse["port"]=GLB_configuration["timelapseServicePort"]
    timelapse["ip"]  =GLB_configuration["timelapseServiceIP"]

    streamer={}
    streamer["port"]=GLB_configuration["mjpg-streamerServicePort"]
    streamer["ip"]  =GLB_configuration["mjpg-streamerServiceIP"]
    st=getStatus()
    rt=render_template('index.html', title="smartCam Site",status=st,streamer=streamer,timelapse=timelapse)
    return rt


'''----------------------------------------------------------'''
def  mountBindMediaPath(mount=True):
  ### Mount in loop mediapath 
  localpath=os.path.dirname(os.path.abspath(__file__))+"/static/tmp/"+os.path.basename(GLB_configuration["mediaPath"])

  try:
        #Create local path
        os.makedirs(localpath)
  except FileExistsError:
        # directory already exists
        pass
  

  try:
    cmd="sudo umount " + localpath
    if mount:
      cmd="sudo mount --bind "+GLB_configuration["mediaPath"]+ " " +localpath

    helper.internalLogger.debug("Mounting in loop mediapath for static flask access:{0}".format(cmd))
    subprocess.call(['bash','-c',cmd]) 
  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.debug('Error: executing {0}. Exception unprocessed properly. Exiting'.format(cmd))
    helper.einternalLogger.exception(e)  



'''----------------------------------------------------------'''
'''----------------       M A I N         -------------------'''
'''----------------------------------------------------------'''

def main(configfile):
  print('smartCam-start -----------------------------')

  # Loading config file,
  # Default values
  cfg_log_traces="smartCam.log"
  cfg_log_exceptions="smartCame.log"


  global GLB_configuration


  # Let's fetch data
  GLB_configuration={}
  with open(configfile) as json_data:
      GLB_configuration = json.load(json_data)
  #Get log names
  if "log" in GLB_configuration:
      if "logTraces" in GLB_configuration["log"]:
        cfg_log_traces = GLB_configuration["log"]["logTraces"]
      if "logExceptions" in GLB_configuration["log"]:
        cfg_log_exceptions = GLB_configuration["log"]["logExceptions"]
  helper.init(cfg_log_traces,cfg_log_exceptions)
  print('See logs traces in: {0} and exeptions in: {1}-----------'.format(cfg_log_traces,cfg_log_exceptions))  
  helper.internalLogger.critical('smartCam-start -------------------------------')  
  helper.einternalLogger.critical('smartCam-start -------------------------------')

  try:
        os.makedirs(GLB_configuration["mediaPath"])
  except FileExistsError:
        # directory already exists
        pass
  
  mountBindMediaPath(False)
  mountBindMediaPath(True)
 
  try:
    apiRestTask=threading.Thread(target=apirest_task,name="restapi")
    apiRestTask.daemon = True
    apiRestTask.start()

  except Exception as e:
    helper.internalLogger.critical("Error processing GLB_configuration json {0} file. Exiting".format(configfile))
    helper.einternalLogger.exception(e)
    loggingEnd()
    return  

  try:    

     while True:
       #helper.internalLogger.critical("Polling, nothing to poll yet")
       time.sleep(1)


  except Exception as e:
    e = sys.exc_info()[0]
    helper.internalLogger.critical('Error: Exception unprocessed properly. Exiting')
    helper.einternalLogger.exception(e)  
    print('smartCam-General exeception captured. See log:{0}',format(cfg_log_exceptions))        
    mountBindMediaPath(False)
    loggingEnd()

'''----------------------------------------------------------'''
'''----------------     apirest_task      -------------------'''
def apirest_task():

  api.run(debug=True, use_reloader=False,port=GLB_configuration["port"],host=GLB_configuration["host"])


'''----------------------------------------------------------'''
'''----------------       loggingEnd      -------------------'''
def loggingEnd():      
  helper.internalLogger.critical('smartCam-end -----------------------------')        
  print('smartCam-end -----------------------------')


'''----------------------------------------------------------'''
'''----------------     parse_args        -------------------'''
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='smartCam service')
    parser.add_argument('--configfile', type=str, required=False,
                        default='/etc/smartCam.conf',
                        help='Config file for the service')
    return parser.parse_args()

'''----------------------------------------------------------'''
'''----------------    printPlatformInfo  -------------------'''
def printPlatformInfo():
    print("Running on OS '{0}' release '{1}' platform '{2}'.".format(os.name,platform.system(),platform.release()))
    print("Uname raw info: {0}".format(os.uname()))
    print("Arquitecture: {0}".format(os.uname()[4]))
    print("Python version: {0}".format(sys.version_info))

'''----------------------------------------------------------'''
'''----------------       '__main__'      -------------------'''
if __name__ == '__main__':
    printPlatformInfo()
    args = parse_args()
    main(configfile=args.configfile)

