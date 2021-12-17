'''
    With Options
'''
import requests
import pycurl
import os, sys, time, base64, commands, json
import urllib
import base64
from StringIO import StringIO
from operator import index
import time,datetime
from datetime import date, timedelta
from __builtin__ import raw_input

API_V2_PREFIX = "/api/v2"
ACCESS_TOKEN_PATH ="/auth/oauth/token"
GRANT_TYPE = "client_credentials"

Log_file = 'templateExp.log'
INFO = 'INFO'
WARN = 'WARN'
ERROR = 'ERROR'
DEBUG = 'DEBUG'

def httpRequest(url, header=[], data={}, delete=False):
    
    """ This httpRequest method is used to call both HTTPPOST and HTTPGET methods. 
    It will gets Access Token info by posting Client_secret, client_id, grant_type info to cloud. 
    """
    
    try:
        headers = ['Accept: application/json']
        headers.extend(header)
        strio = StringIO()
        try:
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER, headers)
            c.setopt(pycurl.VERBOSE, 0)
            c.setopt(pycurl.NOSIGNAL, 1)
            c.setopt(pycurl.TIMEOUT, 500)
            c.setopt(pycurl.CONNECTTIMEOUT, 500)
            c.setopt(pycurl.SSL_VERIFYPEER, False)
            c.setopt(pycurl.SSL_VERIFYHOST, False)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.WRITEFUNCTION, strio.write)
            if delete:
                c.setopt(pycurl.VERBOSE, 0)
                c.setopt(pycurl.POSTFIELDS, data)
                c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
            elif data:
                c.setopt(pycurl.POST, 1)
                c.setopt(pycurl.POSTFIELDS, data)
            else:
                c.setopt(pycurl.HTTPGET, 1)
            
            c.perform()
            
        except Exception, ex:
            raise Exception(str(ex))
        
        content = strio.getvalue()
        response = int(c.getinfo(pycurl.HTTP_CODE))
        if response != 200:
            if response != 404:
                logMessage(ERROR, 'httpRequest', 'postData - Response code ' + str(response) + ' ' + content)
                raise Exception('\t\tpostData - Response code ' + str(response) + ' ' + content)
            else:
                logMessage(ERROR, 'httpRequest', 'postData: HTTP_404 - ' + content)
                raise Exception('\t\tpostData: HTTP_404 - ' + content)
        strio.flush()
        strio.close()
        c.close()
        return content
    except Exception, msg:
        logMessage(ERROR, 'httpRequest', "Exception in httpRequest - " + str(msg))
        raise Exception("\t\tException in httpRequest - " + str(msg))

def getAuthToken(base_url, api_key, api_secret, grant_type):
    try:
        data = {
            'client_secret' : api_secret,
            'grant_type'    : grant_type,
            'client_id'     : api_key
        }
        token_url = base_url + "/auth/oauth/token"
        postResponse = httpRequest(token_url, [], urllib.urlencode(data))
        tokenResponse = json.loads(postResponse)
        return tokenResponse
    except Exception as errMsg:
        logMessage(ERROR, 'getAuthToken', str(errMsg))
        print "\t\t" + str(errMsg)

DEBUG = False
def executeCommand(cmd, args=[], ignoreOnError=False):
    for arg in args:
        cmd = cmd + ' ' + str(arg)
    if DEBUG:
        print "Executing command: " , cmd
    try:
        result = commands.getstatusoutput(cmd)
    except Exception as errmsg:
        return 1, 'Exception caught - ' + str(errmsg)

    if DEBUG:
        print "Command output is : %s , %s " % (result[0] >> 8 ,result[1]) 
    if result[0] != 0 and ignoreOnError == False:
        raise Exception("Failed to execute command: " + cmd)
    return result[0] >> 8 , result[1]

def logMessage(level, message, data):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(Log_file):
        print "Log_file " + Log_file
        cmd = "/usr/bin/sudo /bin/touch " + Log_file
        executeCommand(cmd, [], True)
    cmd = "echo \"" + now + " : " + level + " : " + message + " : " + data + "\" >> " + Log_file + " 2>/dev/null";
    return executeCommand(cmd,[],True)[0] == 0

def invokeDelete(auth, int_id):
    try:
        URL = 'https://test.com//api/v2/installed/'+ int_id
        headers = ["Content-Type: application/json", "Accept: application/json", "Authorization: " + auth]
        data = {"uninstallReason" : "Integration not required"}
        response  = httpRequest(URL, headers, json.dumps(data), delete=True)
    except Exception as errMsg:
        print "error"
        print errMsg

def genAuth(api_base_url, api_key, api_secret, grant_type):
    try:
        auth_token_res = getAuthToken(api_base_url, api_key, api_secret , grant_type)
        access_token = auth_token_res['access_token']
        token_type = auth_token_res['token_type']
        auth = str(token_type) + " " + str(access_token)
        return auth
    except Exception as errMsg:
        logMessage(ERROR, 'genAuth', str(errMsg))

if __name__ == "__main__":
    try:
        count = 0
        SOURCE_API_BASE_URL = "https://test.com"
        SOURCE_API_KEY = ""
        SOURCE_API_SECRET = ""
        source_auth = genAuth(SOURCE_API_BASE_URL, SOURCE_API_KEY, SOURCE_API_SECRET, GRANT_TYPE)
        print source_auth
        with open('input.txt') as f:
            content = f.readlines()
        int_data = [x.strip('\n') for x in content] 
        for int_id in int_data:
            invokeDelete(source_auth, int_id)
            print str(count+1) + " - Integration uninstalled : " + int_id
            count+=1
    except Exception as errMsg:
        logMessage(ERROR, 'main', str(errMsg))
