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
    data = f.read()

pattern_ipv4 = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
ips = re.findall(pattern_ipv4, data)
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


with open('data.json', 'w') as f:
    json.dump(data, f)

# map
coord_data = [np.array(item['loc'].split(','), dtype=np.float64) for item in data]
coord_data = [(item['location']['latitude'], item['location']['longitude']) for item in data]

mymap = folium.Map(location=[20.0, 0.0], zoom_start=2, max_zoom=1)
folium.TileLayer('cartodbdark_matter').add_to(mymap)
folium.plugins.HeatMap(coord_data).add_to(mymap)
folium.plugins.MarkerCluster(
    coord_data,
    show_coverage_on_hover=False,
    spiderfy_distance_multiplier=0
).add_to(mymap)

mymap.save('ip_heatmap.html')
