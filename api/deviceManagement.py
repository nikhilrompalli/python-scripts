#Need to install requests package for python
#easy_install requests
import requests
import pycurl
import json
import urllib
import base64
from StringIO import StringIO

def httpRequest(url, header=[], data={}, delete=False):
    
    """ This httpRequest method is used to call both HTTPPOST and HTTPGET methods. 
    It will gets Access Token info by posting Client_secret, client_id, grant_type info to Vistara cloud. 
    Then will pulls Vistara alerts by invoking Vistara Get Alerts API call. """
    
    try:
        headers = ['Accept: application/json']
        headers.extend(header)
        #logger.info(headers)
        strio = StringIO()
        try:
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER, headers)
            c.setopt(pycurl.VERBOSE, 0)
            c.setopt(pycurl.NOSIGNAL, 1)
            c.setopt(pycurl.TIMEOUT, 120)
            c.setopt(pycurl.CONNECTTIMEOUT, 120)
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
            #logger.error(str(ex))
            raise Exception(str(ex))
            #sys.exit(2)
        
        content = strio.getvalue()
#         print content
#         print("httpRequest response ======= " + content.decode("utf-8"))
        #content = json.loads(content)
        response = int(c.getinfo(pycurl.HTTP_CODE))
#         print(response)
        #print c.getinfo(pycurl.HTTP_CODE), c.getinfo(pycurl.EFFECTIVE_URL)
        if response != 200:
            if response != 404:
                print('postData: Response Code - ' + str(response))
                raise Exception('postData - Response code ' + str(response) + ' ' + content)
            else:
#                 logger.error('postData: HTTP_404 - ' + content)
                raise Exception('postData: HTTP_404 - ' + content)
        strio.flush()
        strio.close()
        c.close()
        return content
    except Exception, msg:
        #logger.info("Exception in httpRequest - " + str(msg))
        raise Exception("Exception in httpRequest - " + str(msg))
    
def SNdeviceData(url):
    print "in SNdeviceData"
    user = 'OrgUser'
    pwd = '0ps5amp01!'
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()
    data = response.json()
    return data

def getAccessToken():
    client_key = ''
    client_secret = ''
    grant_type = 'client_credentials'
    data = {
        'client_secret' : client_secret,
        'grant_type'    : grant_type,
        'client_id'     : client_key
    }
    base_url = "https://test.api.org.com"
    token_url = base_url + "/auth/oauth/token"
    print "getAccessToken url "+token_url
    postResponse = httpRequest(token_url, [], urllib.urlencode(data))
    tokenResponse = json.loads(postResponse)
#     print "access token "+tokenResponse
    access_token = tokenResponse["access_token"]
    print "access token "+access_token
    return access_token

def OrgDeviceData(DeviceUrl):
    print "in OrgDeviceData"
    access_token = getAccessToken()
    
    
    headers = ["Content-Type: application/json", "Accept: application/json", "Authorization: " +  "Bearer " + access_token]
    response  = httpRequest(DeviceUrl, headers)
    data = json.loads(response)
    return data

def unassignDevice(attrId,attrValueId,deviceUuid):
    print "in unassign device"
    url = 'https://test.api.org.com/api/v2/tenants/client_568/customAttributes/'+str(attrId)+'/values/'+str(attrValueId)+'/devices'
    print "unassignDevice url "+url
    access_token = getAccessToken()
    data = [{
        'id' : deviceUuid
    }]
    print "unassignDevice data payload" + str(data)
    headers = ["Content-Type: application/json", "Accept: application/json", "Authorization: " +  "Bearer " + access_token]
    response = httpRequest(url, headers, json.dumps(data), delete=True)
    print response

def createNewValue(AttrID,SNAttrEnv):
    print "create new value "
    url = 'https://env.org.com/api/v2/tenants/client_568/customAttributes/'+str(AttrID)+''
    access_token = getAccessToken()
    data = {
        "customAttributeValues": [{
            "value": SNAttrEnv
        }]
    }
    headers = ["Content-Type: application/json", "Accept: application/json", "Authorization: " +  "Bearer " + access_token]
    response = httpRequest(url, headers, urllib.urlencode(data))
    return response["id"]

def getNewValueId(AttrID,SNAttrEnv):
    print "-----in get new value id------"
    print "SNAttrEnv "+str(SNAttrEnv)
    url = 'https://env.org.com/api/v2/tenants/client_568/customAttributes/'+str(AttrID)+''
    access_token = getAccessToken()
    headers = ["Content-Type: application/json", "Accept: application/json", "Authorization: " +  "Bearer " + access_token]
    response = httpRequest(url, headers, {})
    print "response "+str(response)
    data = json.loads(response)
    print "response[customAttributeValues] "+ str(data["customAttributeValues"])
    for custAttrVal in data["customAttributeValues"]:
        if custAttrVal["value"] == SNAttrEnv.lower():
            return custAttrVal["id"]
    '''custAttrVal is not found in org,creating new value'''
    res = createNewValue(AttrID,SNAttrEnv)
    print "new create device "+str(res)
    return res
    
def assignDevice(AttrValueID,AttrID,SNAttrEnv):
    print "in assign device"
    custAttrValueId = getNewValueId(AttrID,SNAttrEnv)
    print "deviceId "+str(deviceId)
    url = 'https://test.api.org.com/api/v2/tenants/client_568/customAttributes/'+str(AttrID)+'/values/'+str(AttrValueID)+'/devices'
    print "assign device url "+url
    access_token = getAccessToken()
    data = [{
        'id' : deviceId
    }]
    headers = ["Content-Type: application/json", "Accept: application/json", "Authorization: " +  "Bearer " + access_token]
    response = httpRequest(url, headers, json.dumps(data))
    print "assign device response "+str(response)

def getSNAttrName(url):
    print "in getSNAttrName"
    user = ''
    pwd = ''
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()
    data = response.json()
    return data["result"]["name"]

def main():
    attr = [{"attributeName":"IT Owner","attributeId": "13218","attributeFieldName": "assigned_to"},
            {"attributeName" : "Support Group", "attributeId": "13223","attributeFieldName": "support_group"},
            {"attributeName" : "Business Owner", "attributeId": "13238","attributeFieldName": "u_business_owner_grp"},
            {"attributeName" : "Environment", "attributeId": "13233","attributeFieldName": "u_environment"}
           ]
    SNdeviceUrl = 'https://testamericasdev.service-now.com/api/now/table/cmdb_ci'
    SNResponseData = SNdeviceData(SNdeviceUrl)
    for SNDEvice in SNResponseData["result"]:
        OrgDeviceUuid = SNDEvice["u_org_resource_id"]
        SNAttrEnv = SNDEvice["u_environment"]
        SNBussUrl = SNDEvice["u_business_owner_grp"]["link"]
        SNSupportUrl = SNDEvice["support_group"]["link"]
        SNItOwnerUrl = SNDEvice["assigned_to"]["link"]
#         SNAttrBussOwner = SNDEvice["u_business_owner_grp"]
        SNEnvAttrName = SNDEvice["u_environment"]
        SNBussAttrName = getSNAttrName(SNBussUrl)
        SNSupportAttrName = getSNAttrName(SNSupportUrl)
        SNItOwnerAttrName = getSNAttrName(SNItOwnerUrl)
        OrgDeviceDetailsUrl= 'https://env.org.com/api/v2/tenants/client_568/devices/'+OrgDeviceUuid+'/customAttributes'
        OrgResponseData = OrgDeviceData(OrgDeviceDetailsUrl)
        print "OrgResponseData "+str(OrgResponseData)
        for custAttr in OrgResponseData:
            OrgCustAttrName = custAttr["customAttributeValue"]["customAttribute"]["name"]
            OrgCustAttrID = custAttr["customAttributeValue"]["customAttribute"]["id"]
            OrgCustAttrValue = custAttr["customAttributeValue"]["value"]
            OrgCustAttrValueId = custAttr["customAttributeValue"]["id"]
            if OrgCustAttrName == "Environment":
                if SNEnvAttrName != OrgCustAttrValue:
                    unassignDevice(OrgCustAttrID,OrgCustAttrValueId,OrgDeviceUuid)
                    assignDevice(OrgCustAttrValueId,OrgCustAttrID,SNEnvAttrName)
            elif OrgCustAttrName == "Business Owner":
                if SNBussAttrName != OrgCustAttrValue:
                    unassignDevice(OrgCustAttrID,OrgCustAttrValueId,OrgDeviceUuid)
                    assignDevice(OrgCustAttrValueId,OrgCustAttrID,SNBussAttrName)
            elif OrgCustAttrName == "IT Owner":
                if SNItOwnerAttrName != OrgCustAttrValue:
                    unassignDevice(OrgCustAttrID,OrgCustAttrValueId,OrgDeviceUuid)
                    assignDevice(OrgCustAttrValueId,OrgCustAttrID,SNItOwnerAttrName)
            elif OrgCustAttrName == "Support Group":
                if SNSupportAttrName != OrgCustAttrValue:
                    unassignDevice(OrgCustAttrID,OrgCustAttrValueId,OrgDeviceUuid)
                    assignDevice(OrgCustAttrValueId,OrgCustAttrID,SNSupportAttrName)

    
if __name__ == "__main__":
    main() 
