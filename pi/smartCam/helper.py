import logging
import sys
import os

def init(tracePath="/var/log/em.log",exceptionsPath="/var/log/em.log",il="il",eil="eil"):
  global internalLogger
  internalLogger = logging.getLogger(il)
  hdlr_1 = logging.FileHandler(tracePath)
  formatter_1 = logging.Formatter('%(asctime)s %(processName)s %(levelname)-8s %(threadName)-10s %(funcName)12s() %(message)s')
  hdlr_1.setFormatter(formatter_1)
  internalLogger.addHandler(hdlr_1)
  internalLogger.setLevel(logging.DEBUG)

  # Logging with exceptions 
  global einternalLogger
  einternalLogger  = logging.getLogger(eil)
  hdlr_1 = logging.FileHandler(exceptionsPath)
  formatter_1 = logging.Formatter('%(asctime)s %(processName)s %(levelname)-8s %(threadName)-10s %(funcName)12s() %(message)s')
  hdlr_1.setFormatter(formatter_1)
  einternalLogger.addHandler(hdlr_1)
  einternalLogger.setLevel(logging.DEBUG)

def amIaPi():
  rt=False
  if "arm" in os.uname()[4]:
    rt=True
  return rt

