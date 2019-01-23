import csv
import json
import sys
import time
import threading
import os
import re

from random import SystemRandom

from apps import action
from apps.messaging import Text, Message, send_message, Url, AcceptDecline
from walkoff.executiondb.device import get_device_ids_by_fields


@action
def get_devices_by_fields(fields):
    return get_device_ids_by_fields(fields)


@action
def system_rand():
    return SystemRandom().random()


@action
def round_to_n(number, places):
    return round(number, places)


@action
def echo_object(data):
    return data


@action
def echo_array(data):
    return data


@action
def csv_as_array(data):
    return data.split(",")


@action
def json_select(json_reference, element):
    return json.loads(json_reference)[element]


@action
def list_select(list_reference, index):
    return json.loads(list_reference)[index]


@action
def linear_scale(value, min_value, max_value, low_scale, high_scale):
    fraction_of_value_range = (min((min((value - min_value), min_value) / (max_value - min_value)), 1.0))
    return low_scale + fraction_of_value_range * (high_scale - low_scale)


@action
def divide(value, divisor):
    return value / divisor


@action
def multiply(value, multiplier):
    return value * multiplier


@action
def add(num1, num2):
    return num1 + num2


@action
def subtract(value, subtractor):
    return value - subtractor


@action
def pause(seconds):
    time.sleep(seconds)
    return 'success'


@action
def write_ips_to_csv(ips_reference, path):
    ips = json.loads(ips_reference)

    if sys.version_info[0] == 2:
        with open(path, 'wb') as csvfile:
            fieldnames = ['Host', 'Up']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for ip in ips:
                if ips[ip] == "up":
                    writer.writerow({'Host': ip, 'Up': 'X'})
                else:
                    writer.writerow({'Host': ip})
    else:
        with open(path, 'w', newline='') as csvfile:
            fieldnames = ['Host', 'Up']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for ip in ips:
                if ips[ip] == "up":
                    writer.writerow({'Host': ip, 'Up': 'X'})
                else:
                    writer.writerow({'Host': ip})


@action
def send_text_message(subject, message, users=None, roles=None):
    text = Text(message)
    message = Message(subject=subject, body=[text])
    send_message(message, users=users, roles=roles)
    return 'success'


@action
def basic_request_user_approval(users=None, roles=None):
    text = Text('A workflow requires your authentication')
    message = Message(subject='Workflow awaiting approval', body=[text, AcceptDecline()])
    send_message(message, users=users, roles=roles)
    return 'success'


@action
def create_text_message_component(text):
    return Text(text).as_json()


@action
def create_url_message_component(url, title=None):
    return Url(url, title=title).as_json()


@action
def create_accept_decline_message_component():
    return AcceptDecline().as_json()


@action
def create_empty_message(subject=None):
    return Message(subject=subject).as_json()


@action
def append_text_message_component(message, text):
    message = Message.from_json(message)
    message.append(Text(text))
    return message.as_json()


@action
def append_url_message_component(message, url, title=None):
    message = Message.from_json(message)
    message.append(Url(url, title=title))
    return message.as_json()


@action
def append_accept_decline_message_component(message):
    message = Message.from_json(message)
    message.append(AcceptDecline())
    return message.as_json()


@action
def combine_messages(message1, message2):
    message1 = Message.from_json(message1)
    message1 += Message.from_json(message2)
    return message1.as_json()


@action
def set_message_subject(message, subject):
    message = Message.from_json(message)
    message.subject = subject
    return message.as_json()


@action
def send_full_message(message, users=None, roles=None):
    message = Message.from_json(message)
    send_message(message, users=users, roles=roles)
    return 'success'


@action
def accept_decline(action):
    r = action.lower() == 'accept'
    return r, "Accepted" if r else "Declined"


@action
def csv_to_json(path, separator=',', encoding='ascii', headers=None):
    import sys
    if sys.version[0] == '2':
        from io import open
    try:
        with open(path, encoding=encoding) as f:
            results = []
            if not headers:
                headers = f.readline().split(separator)
            for line in f.readlines():
                line = line.strip('\r\n')
                results.append({key: value for key, value in zip(headers, line.split(','))})
        return results
    except (IOError, OSError) as e:
        return e, 'File Error'


@action
def mark_blacklist(data, blacklisted=True):
    for element in data:
        element['blacklisted'] = blacklisted
    return data, 'Success'


@action
def mark_whitelist(data, whitelisted=True):
    for element in data:
        element['whitelisted'] = whitelisted
    return data, 'Success'


@action
def mark_whitelist_blacklist(data, whitelisted=False, blacklisted=False):
    for element in data:
        element.update({'whitelisted': whitelisted, 'blacklisted': blacklisted})


@action
def is_string_in_file(file, str_to_find):
    try:
        if str_to_find in open(file).read():
            return True, 'Success'
        else: return False, 'Success'
    except IOError:
        return False, 'File Error'


def threading_wait(fullPath, timeToWait):
    x = 0
    while x < 10: #intended to be infinite
        time.sleep(timeToWait)
        if os.path.getsize(fullPath) > 0:
            print('FIle size not 0')
            return


@action
def check_file_not_empty(fullPath, interval):
    t = threading.Thread(target=threading_wait(fullPath, int(interval)))
    t.start()
    return 'Success'


@action
def clear_lines_containing_strings(filePath, targetStrings):
    removedLines = []
    with open(filePath, 'r+') as f:
        lines = f.readlines()
        numLines = len(lines)
        for x in range(0, numLines):
            for y in targetStrings:
                if y in lines[x]:
                    if x not in removedLines:
                        removedLines.append(x)

        f.seek(0)
        for x in range(0, numLines):
            if x not in removedLines:
                f.write(lines[x])
        f.truncate()
    return 'Success'

@action
def extract_ip_from_file(filepath):
    #pattern = '^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))$'
    pattern = '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    ipGroup = []
    with open(filepath, 'r') as f:
        for line in f:
            ip = re.search(pattern, line)
            if ip:
                #prevent duplicate IPs from being extracted
                if ip.group() not in ipGroup:
                    ipGroup.append(ip.group())
    if ipGroup:
        #space seperate the ips and return as string
        return ' '.join(ipGroup), 'Success'
    return 'NoIPFound'


