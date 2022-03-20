import os
import requests
import json
from re import search
from random import randint


# 登录校园网
def xywlogin(username:str, password:str, ispcode:str, PATH:str) -> bool:
    cachedict = {"current_user_agent": "", "macid": "", "v46ip": ""}
    user_agent = []
    username = str(username)
    password = str(password)
    with open(f'{PATH}/units/user_agent.txt') as f:
        for line in f:
            curruagent = line[:-1]
            user_agent.append(curruagent)
    curruagent = user_agent[randint(0,len(user_agent)-1)]
    cachedict["current_user_agent"] = curruagent

    url = 'http://10.255.0.19/a79.htm'
    headers = {
        'User-Agent': curruagent,
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Host': '10.255.0.19'
    }
    payload = f'DDDDD={username}{ispcode}&upass={password}\
&0MKKey=123456&R1=0&R3=0&R6=0&para=00&v6ip=&v=' + str(randint(1500,8500))
    requests.post(url=url,headers=headers,data=payload)

    headers = {
        "Host": "10.255.0.19",
        "Connection": "keep-alive",
        "User-Agent": curruagent,
        "Accept": "*/*",
        "Referer": "http://10.255.0.19/a79.htm",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    url = f'http://10.255.0.19/drcom/login?callback=dr1003\
&DDDDD={username}{ispcode}&upass={password}&0MKKey=123456\
&R1=0&R3=0&R6=0&para=00&v6ip=&v=' + str(randint(1500,8500))
    resp = requests.get(url=url, headers=headers)

    macid = search('(?<="olmac":")([\s\S]+?)(?=",)', resp.text).group(1)
    cachedict["macid"] = macid
    v46ip = search('(?<="v46ip":")([\s\S]+?)(?=",)', resp.text).group(1)
    cachedict["v46ip"] = v46ip
    with open(f'{PATH}/.temp/.cache', 'w') as f:
        json.dump(cachedict, f)

    result = search('(?<="result":)([0-9])(?=,)', resp.text).group(1)
    if result:
        status = True
    else:
        status = False

    return status


# 登出校园网
def xywlogout(username:str, cachedict:dict):
    louturl = f'http://10.255.0.19:801/eportal/?c=Portal&a=unbind_mac\
&callback=dr1003&user_account={username}&wlan_user_mac={cachedict["macid"]}\
&wlan_user_ip={cachedict["v46ip"]}&jsVersion=3.3.2&v=' + str(randint(1500,8500))

    cbackurl = 'http://10.255.0.19/drcom/logout?callback=dr1004&v=' + str(randint(1500,8500))
    headers = {
        "Host": "10.255.0.19:801",
        "Connection": "keep-alive",
        "User-Agent": cachedict["current_user_agent"],
        "Accept": "*/*",
        "Referer": "http://10.255.0.19/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    resp = requests.get(url=louturl,headers=headers)

    headers = {
        "Host": "10.255.0.19",
        "Connection": "keep-alive",
        "User-Agent": cachedict["current_user_agent"],
        "Accept": "*/*",
        "Referer": "http://10.255.0.19/a79.htm",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    resp = requests.get(cbackurl,headers=headers)
    result = search('(?<="result":)([0-9])(?=,)', resp.text).group(1)

    if result:
        Status = False
    else:
        Status = True

    return Status


# 判断网络状态 get请求223.6.6.6,返回404为连通,校园网未登录状态因ip劫持将返回200
def whatstatus() -> bool:
    status = True
    url = 'http://223.6.6.6'
    try:
        resp = requests.get(url, timeout=1.5)
        print(resp.status_code)
        if resp.status_code == 404:
            status = True
        else:
            status = False
    except requests.exceptions.Timeout:
        status = False

    return status