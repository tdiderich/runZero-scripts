#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    findDupes.py, version 1.2 by Derek Burke
    Query runZero API for all assets found within an Organization (tied to Export API key provided) and sort out assets with
    same MAC, Hostname, and IP but different asset ID. Optionally, an output file format can be specified to write to."""

import json
import re
import requests
import sys
from datetime import datetime
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    findDupes.py [arguments]

                    You will be prompted to provide your runZero Export API key unless a
                    configuration file is specified as an argument.
                    
                    Optional arguments:

                    -u <uri>                URI of console (default is https://console.runzero.com)
                    -t <time span>          Time span to search for new assets e.g. 1day, 2weeks, 1month.
                                            If used in conjunction with config will take precedence over config value.
                    -c <config file/path>   Filename of config file including absolute path.
                    -o <text| json | all>   Output file format for report. JSON is default.
                    -g                      Generate config file template.
                    -h                      Show this help dialogue
                    
                Examples:
                    findDupes.py -c example.config
                    findDupes.py -c example.config -o json
                    python3 -m findDupes -u https://custom.runzero.com -t 1week""")

def genConfig():
    """Create a template for script configuration file."""

    template = "exportToken= #Export API Key\nuri=https://console.runzero.com #Console URL\ntime=7days #Time span for query in runZero syntax\n"
    writeFile("config_template", template)
    exit()

def readConfig(configFile):
    """ Read values from configuration file

        :param config: a file, file containing values for script
        :returns: a tuple, console url at index 0, API token at index 1, and time query at index 2.
        :raises: IOError: if file cannot be read.
        :raises: FileNotFoundError: if file doesn't exist."""
    try:
        with open( configFile, 'r') as c:
            config = c.read()
            url = re.search("uri=(http[s]?://[a-z0-9.]+)", config).group(1)
            token = re.search("exportToken=([0-9A-Z]+)", config).group(1)
            time = re.search("time=([0-9]*[a-z]+)", config).group(1)
            return(url, token, time)
    except IOError as error:
        raise error
    except FileNotFoundError as error:
        raise error
    
def getAssets(uri, token, filter=" ", fields=" "):
    """ Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param uri: A string, URI of runZero console.
        :param token: A string, Export API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :param fields: A string, comma separated string of fields to return(" " returns all).
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console."""

    uri = uri + "/api/v1.0/export/org/assets.json?"
    params = {'search': filter,
              'fields': fields}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer %s' % token}
    try:
        response = requests.get(uri, headers=headers, params=params, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def findDupes(data):
    """ Parse runZero asset data (JSON) to find potential duplicates. 
    
        :param data: a dict, JSON formatted runZero asset data.
        :raises: KeyError: if key:value pair not present in asset data. """
    #Create list of assets(dicts) with unique IDs
    try:
        uniqIDs = []
        for item in data:
            count = 0
            for asset in uniqIDs:
                if item['id'] == asset['id']:
                    count += 1
            if count == 0: 
                uniqIDs.append(item)
    except KeyError as error:
        raise error
    #Loop through unique IDs and identify assets that identical MACs, Hostnames, and/or IPs
    #Add these assets with duplicate fields to list
    possblDups = []
    try:
        for asset in uniqIDs:
            uid = asset['id']
            macs = asset['macs']
            addresses = asset['addresses']
            hostnames = asset['names']
            for others in uniqIDs:
                #So asset doesn't match itself as a duplicate
                if uid == others['id']:
                    pass
                else:
                    macMatch = False
                    addrMatch = False
                    nameMatch = False
                    matchedMACs = []
                    matchedAddresses = []
                    matchedHostnames = []  
                    for mac in others['macs']:
                        if mac in macs:
                            macMatch = True
                            matchedMACs.append(mac)
                    for addr in others['addresses']:
                        if addr in addresses:
                            addMatch = True
                            matchedAddresses.append(addr)
                    for name in others['names']:
                        if name in hostnames:
                            nameMatch = True
                            matchedHostnames.append(name)
                    if macMatch or addrMatch or nameMatch:
                        asset['possible_dupe'] = {'id': others['id'], 'os': others['os'], 'hw': others['hw']}
                        asset['shared_fields'] = {'MAC': macMatch,
                                                  'matched_MACs': matchedMACs,  
                                                  'IP address': addrMatch, 
                                                  'matched_Addresses': matchedAddresses, 
                                                  'Hostname': nameMatch, 
                                                  'matched_Hostnames': matchedHostnames, 
                                                  'site': others['site_id']}
                        possblDups.append(asset)
        if len(possblDups) > 0:
            return possblDups
        else:
            return({"Msg": "No potential duplicate assets found."})
    except KeyError as error:
        raise error
    
def writeFile(fileName, contents):
    """ Write contents to output file in plaintext. 
    
        :param filename: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file. """
    try:
        with open( fileName, 'w') as o:
                    o.write(contents)
    except IOError as error:
        raise error
    
if __name__ == "__main__":
    if "-h" in sys.argv:
        usage()
        exit()
    if "-g" in sys.argv:
        genConfig()
    config = False
    configFile = ''
    consoleURL = 'https://console.runzero.com'
    token = ''
    timeRange = ' '
    #Output report name; default uses UTC time
    fileName = "Duplicate_Asset_Report_" + str(datetime.utcnow())
    #Define config file to read from
    if "-c" in sys.argv:
        try:
            config = True
            configFile =sys.argv[sys.argv.index("-c") + 1]
            confParams = readConfig(configFile)
            consoleURL = confParams[0]
            token = confParams[1]
            timeRange = confParams[2]
        except IndexError as error:
            print("Config file switch used but no file provided!\n")
            usage()
            exit()
    else:
        print("Enter your Export API Key: ")
        token = getpass()
    if "-u" in sys.argv and not config:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
            usage()
            exit()
    if "-t" in sys.argv:
        try:
            timeRange = sys.argv[sys.argv.index("-t") + 1]
        except IndexError as error:
            print("time range switch used but time range not provided!\n")
            usage()
            exit()
    fields = "id, os, hw, addresses, macs, names, alive, site_id" #fields to return in API call; modify for more or less
    assets = getAssets(consoleURL, token, 'first_seen:<' + timeRange, fields)
    dupes = findDupes(assets)
    if "-o" in sys.argv and sys.argv[sys.argv.index("-o") + 1].lower() not in ('text', 'txt', 'all'):
        writeFile(fileName + '.json', json.dumps(dupes, indent=4))
    elif "-o" in sys.argv and sys.argv[sys.argv.index("-o") + 1].lower() in ('text', 'txt'):
        stringList = []
        for line in dupes:
                stringList.append(str(line))
        textFile = '\n'.join(stringList)
        writeFile(fileName + '.txt', textFile)
    elif "-o" in sys.argv and sys.argv[sys.argv.index("-o") + 1].lower() == 'all':
        writeFile(fileName + '.txt', '\n'.join(dupes))
        writeFile(fileName + '.json', json.dumps(dupes, indent=4))
    else:
        print(json.dumps(dupes, indent=4))