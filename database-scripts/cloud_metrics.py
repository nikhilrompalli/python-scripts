import mysql.connector
import json

mydb = mysql.connector.connect(
  host="",
  user="root",
  passwd="root",
  database="metrics"
)

def getQueryRes(query):
    try:
        mycursor = mydb.cursor()
        mycursor.execute(query)
        res = mycursor.fetchall()
        return res
    except Exception as err:
        print err

def getCloudMetricsJsonRes(data, services):
    try:
        query = "desc cloud_metrics"
        col = getQueryRes(query)
        json_dict = {}
        for r in range(len(col)):
            if col[r][0] == 'service_id':
                json_dict[col[r][0]] = services
            else:
                json_dict[col[r][0]] = data[r] 
        return json_dict
    except Exception as err:
        print "getCloudMetricsJsonRes error"
        print err

def getServiceJsonRes(data, mt):
    try:
        res = []
        query = "desc services"
        col = getQueryRes(query)
        for row in data:
            json_dict = {}
            for r in range(len(col)):
                if col[r][0] == 'name':
                    json_dict[col[r][0]] = mt
                else:
                    json_dict[col[r][0]] = row[r]
            res.append(json_dict)
        return res
    except Exception as err:
        print "getServiceJsonRes error"
        print err

def getMetricTypeJsonRes(data):
    try:
        res = []
        query = "desc metric_types"
        col = getQueryRes(query)
        for row in data:
            json_dict = {}
            for r in range(len(col)):
                json_dict[col[r][0]] = row[r]
            res.append(json_dict)
        return res
    except Exception as err:
        print "getMetricsTypeJsonRes error"
        print err

try:
    query = 'select distinct(resource_type) from cloud_metrics order by resource_type;'
    res = getQueryRes(query)
    resource_type = 116
    resource_type_res = []
    query = 'select * from cloud_metrics where resource_type=%s' % resource_type
    cm_res = getQueryRes(query)
    for cloud_metrics in cm_res:
        service_id = cloud_metrics[3]
        query = 'select * from services where id=%s' % service_id
        s_res = getQueryRes(query)
        service_name = s_res[0][2]
        query = "select * from metric_types where metric_name ='%s'" % service_name
        mt_res = getQueryRes(query)
        mt_json = getMetricTypeJsonRes(mt_res)
        mt = json.dumps(mt_json)
        s_json = getServiceJsonRes(s_res, mt_json)
        services = json.dumps(s_json)
        cm_json = getCloudMetricsJsonRes(cloud_metrics, s_json)
        cm = json.dumps(cm_json)
        print cm
        print "\n"
        resource_type_res.append(cm)
        
    print resource_type_res
        
    
except Exception as err:
    print "main error"
    print err
    