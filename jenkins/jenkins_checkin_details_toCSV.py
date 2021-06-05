'''
This script is used to get the checking details from jenkins and save into csv file
'''

'''
Packages to install:
    1. pip install xlrd
    2. pip install xlutils
'''

import os,json,sys,time
from datetime import datetime
import pycurl, StringIO
import smtplib, mimetypes
import commands
import xlwt
import os.path
from os import path
from  xlrd import open_workbook
from xlutils.copy import copy
from optparse import OptionParser

#VARIABLES
JENKINS_HOST = ''
JENKINS_PORT = '8888'
CHANGELOG_URL = "http://%s:%s/job/%s/%s/api/json"

header_style = 'pattern: pattern solid, fore_colour orange;'

csv_file = 'jenkins_checkin_details_sheet.xls'

try:

    parser = OptionParser(description="Save Jenkins checkin details to csv.")

    parser.add_option("-j", "--Jenkinspipeline_name", dest="jenkins_pipeline",help="specify the jenkinspipeline name")
    parser.add_option("-b", "--Build_no", dest="build_no",help="Build number to ge the jenkins checkin Details")
    (options, args) = parser.parse_args()

    build_no = options.build_no
    jenkins_pipeline = options.jenkins_pipeline

except Exception, e:
    print "Unexpected Exception [", e.__repr__(), "]"
    sys.exit(3)
    
if len(sys.argv) == 1:
   parser.print_help()
   sys.exit()


def executeCommand(cmd, args=[], ignoreOnError=False):
    for arg in args:
        cmd = cmd + ' ' + str(arg)
    try:
        result = commands.getstatusoutput(cmd)
    except Exception as errmsg:
        return 1, 'Exception caught - ' + str(errmsg)
    
    if result[0] != 0 and ignoreOnError == False:
        raise Exception("Failed to execute command: " + cmd)
    return result[0] >> 8 , result[1]

def fetchChangeLog(job_name, build_no):
    try:
        url = CHANGELOG_URL % (JENKINS_HOST, JENKINS_PORT, job_name, build_no)
        cmd = "curl -s "+ url 
        result = executeCommand(cmd, [], True)
        responseData = json.loads(result[1])
        change_list = [build_no]
        if responseData["changeSets"] == []:
            return True, change_list
        commit_list = responseData["changeSets"][0]["items"]
        for commit in commit_list:
            author = commit["author"]["fullName"]
            comment = commit["comment"]
            change_list.append([author,comment])
        return True, change_list
    except Exception as err:
        print err
        return False, []

def saveChangesTOCsv(sheet, pos, change_list):
    try:
        build_no = change_list[0]
        sheet.write(pos, 0, build_no)
        commit_list = []
        for index in range(1,len(change_list)):
            author = change_list[index][0]
            comment = change_list[index][1]
            data = "author : %s \ncomment : %s\n\n" % (author, comment)
            commit_list.append(data)
        sheet.write(pos, 1, commit_list)
    except Exception as err:
        print err

try:
    status, change_list = fetchChangeLog(jenkins_pipeline, build_no)
    if path.isfile(csv_file):
        rb = open_workbook(csv_file)
        sheet = rb.sheet_by_index(0) 
        row = sheet.nrows
        wb = copy(rb)
        checkin_details_sheet = wb.get_sheet(0) 
        saveChangesTOCsv(checkin_details_sheet, row, change_list)
        wb.save(csv_file)
    else:
        workbook = xlwt.Workbook(encoding = 'latin-1')
        checkin_details_sheet = workbook.add_sheet('Shivalik')
        checkin_details_sheet.write(0, 0, "Build No", xlwt.Style.easyxf(header_style))
        checkin_details_sheet.write(0, 1, "Commit Details", xlwt.Style.easyxf(header_style))
        saveChangesTOCsv(checkin_details_sheet, 1, change_list)
        workbook.save(csv_file)
except Exception as err:
    print err
