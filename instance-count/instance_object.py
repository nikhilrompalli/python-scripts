#!/usr/bin/env python 2.7
'''
/*
 * This script to used to get the instance count from the instance object JSON payload
 * based on the below conditions
 * Objects created before a number of days provided.
 * Objects that only match the pattern.
 */
'''

import sys, json
from optparse import OptionParser
from dateutil import parser
from pandas.core.algorithms import isin

try:
    arg_parser = OptionParser(description="Instance Details")

    arg_parser.add_option("-n", "--no_of_days", dest="no_of_days",help="Specify number of days")
    arg_parser.add_option("-p", "--pattern", dest="matching_pattern",help="Specify match pattern")
    (options, args) = arg_parser.parse_args()

    no_of_days = options.no_of_days
    matching_pattern = options.matching_pattern

except Exception, err:
    print "Unexpected Exception [", err.__repr__(), "]"
    print err
    sys.exit(3)

print len(sys.argv)
if len(sys.argv) != 5:
    print len(sys.argv)
    arg_parser.print_help()
    sys.exit()

instance_json_payload = 'metadata.json'
isFound = 0

'''
/* This method is used search the matching pattern
'''
def get_matching_data(payload, matching_pattern):
    try:
        global isFound
        if isinstance(payload, unicode):
            if matching_pattern in payload:
                isFound = 1
                return 1
            else:
                return 0
        else:
            for val in payload:
                if isinstance(payload[val], unicode) and matching_pattern in payload[val]:
                    isFound = 1
                    break
                elif isinstance(payload[val], list):
                    for ind in payload[val]:
                        get_matching_data(ind, matching_pattern)
        return isFound
    except Exception, err:
        print "Unexpected Exception at get_matching_data : " + str(err)
        return 0
    
'''
/* This method is used to load the json data from file
'''
def loadJsonPayload():
    try:
        with open(instance_json_payload) as json_file:
            data = json.load(json_file)
            max_date_inst_obj = max(data, key=lambda timestamp: parser.parse(timestamp['creationTimestamp']))
        return max_date_inst_obj, data
    except Exception, err:
        print "Unexpected Exception at loadJsonPayload : " + str(err)
        return {}
        
def main():
    try:
        count = 0
        max_date_inst_obj, instance_paylod = loadJsonPayload()
        max_timestamp = max_date_inst_obj["creationTimestamp"]
        for payload in instance_paylod:
            isFound = 0
            delta = parser.parse(max_timestamp) - parser.parse(payload["creationTimestamp"])
            if delta.days - int(no_of_days) >= 0:
                isMatch = get_matching_data(payload, matching_pattern)
                if isMatch == 1:
                    count+= 1
        print "Total objects found : " + str(count)
    except Exception, err:
        print "Unexpected Exception at main : " + str(err)

if __name__ == '__main__':
    main()