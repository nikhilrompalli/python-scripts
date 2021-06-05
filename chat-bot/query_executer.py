'''
    This script is used to execute the SELECT query and returns the output in file.
'''
import json, commands

query = 'SELECT * FROM apps'
mysql_server_ip = '127.0.0.1'
mysql_user = 'root'
mysql_pass = 'root'


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

file_name = 'nikhil'
query_table = 'msp'
query_to_file_cmd = "mysql -u%s -p%s %s -e '%s' > /tmp/%s.txt" % (mysql_user, mysql_pass, query_table, query, file_name)
print query_to_file_cmd
cmd = "salt-ssh -i -l info mysqldb%s* cmd.run \"%s\"" % (mysql_server_ip.split('.')[3], query_to_file_cmd)
print cmd
res = executeCommand(cmd,[],True)
print res