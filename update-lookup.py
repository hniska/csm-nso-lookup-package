#!/usr/bin/env python

import json
import requests
import time
import argparse
import os

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

AUTH = ("admin", "admin")
NSO = 'http://198.18.134.28:8080'
HEADERS = {'Content-Type': 'application/vnd.yang.collection+json',
           'Accept': 'application/vnd.yang.collection+json'}


def is_updated():
    last_modified_url = NSO + '/restconf/data/csm-lookup:csm-lookup/last-modified'
    previously_modified = ''
    # modified_file = '/tmp/csm-lookup-last-modified.txt'
    modified_file = 'csm-lookup-last-modified.txt'

    try:
        with open(modified_file, 'r') as timefile:
            previously_modified = timefile.readline()
    except FileNotFoundError:
        print('No last modified time file found')

    resp = requests.get(last_modified_url, auth=AUTH, headers=HEADERS)
    r = resp.content
    if resp.status_code == 200:
        r_json = json.loads(r)
        last_modified = r_json['csm-lookup:last-modified']
        if previously_modified != last_modified:
            with open(modified_file, 'w') as timefile:
                timefile.write(r_json['csm-lookup:last-modified'])
            return True
    else:
        print(str(resp.status_code) + ' Not Found.\n' + \
             'URL: ' + NSO + '/restconf/data/csm-lookup:csm-lookup/last-modified')
    return False


def generate_lookup():
    # Remember to change lookup_file path, Situation Manager default is $MOOGSOFT/config/lookups
    # i.e lookup_file = '/usr/share/moogsoft/config/lookups/device-to-service.lookup'

    lookup_file = '/usr/share/moogsoft/config/lookups/device-to-service.lookup'
    url = NSO + '/restconf/data/csm-lookup:csm-lookup/device-to-service'

    if is_updated():
        resp = requests.get(url, auth=AUTH, headers=HEADERS)
        r = resp.content
        if resp.status_code == 200:
            r_json = json.loads(r)
            lookup = {}
            with open(lookup_file, 'w') as jsonfile:
                for entry in r_json['collection']['csm-lookup:device-to-service']:
                    lookup_entry = {}
                    for key in entry.keys():
                        if key != 'device':
                            lookup_entry[key] = entry[key]
                    lookup[entry['device']] = lookup_entry
                json.dump(lookup, jsonfile, indent=4, sort_keys=True)


def schedule(sleep_time):
    start_time = time.time()
    while True:
        generate_lookup()
        time.sleep(sleep_time - ((time.time() - start_time) % sleep_time))
        #print('sleep: ' + str(sleep_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timer", nargs='?', default="run-only-once")
    args = parser.parse_args()

    if args.timer == 'run-only-once':
        generate_lookup()
    elif len(os.popen('pgrep -f update-lookup.py').read().strip().split('\n')) == 1:
        schedule(float(args.timer))
    else:
        pids = os.popen('pgrep -f update-lookup.py').read().strip()
        print("update-lookup.py already running, pids: \n " + str(pids))
