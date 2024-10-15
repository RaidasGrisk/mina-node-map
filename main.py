import folium
from folium.plugins import HeatMap
import re
import numpy as np
import asyncio
import aiohttp
import json
import requests


# read data source file
with open('ips.txt', 'r') as f:
    logs = f.read()

pattern_ipv4 = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
ips = re.findall(pattern_ipv4, logs)
ips = list(set(ips))

def fetch_from_ipinfo():
    async def fetch_all_ips(ip_list):

        async def fetch_ip_data(ip, session):
            async with session.get(f'https://ipinfo.io/{ip}/geo') as response:
                return await response.json() if response.status == 200 else None

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
            tasks = [fetch_ip_data(ip, session) for ip in ip_list]
            return await asyncio.gather(*tasks)

    # fetch ip data
    data = asyncio.run(fetch_all_ips(ips))
    return data


def fetch_from_ipapis():
    data = []
    for i in range(0, len(ips), 100):
        print(i)
        response = requests.post(
            url='https://api.ipapi.is',
            params={'key': '1baa2deebf363c56'},
            json={'ips': ips[i:i+100]}
        )
        response_ = response.json()
        for ip in response_.keys():
            if isinstance(response_[ip], dict):
                data.append(response_[ip])
    return data


data = fetch_from_ipapis()
for item in data:
    item.pop('ip', None)

with open('data.json', 'w') as f:
    json.dump(data, f)
