import folium
from folium.plugins import HeatMap
import re
import numpy as np
import asyncio
import aiohttp


# read data source file
with open('ips.txt', 'r') as f:
    data = f.read()

pattern_ipv4 = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
ips = re.findall(pattern_ipv4, data)
ips = list(set(ips))


async def fetch_all_ips(ip_list):

    async def fetch_ip_data(ip, session):
        async with session.get(f'https://ipinfo.io/{ip}/geo') as response:
            return await response.json() if response.status == 200 else None

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
        tasks = [fetch_ip_data(ip, session) for ip in ip_list]
        return await asyncio.gather(*tasks)

# fetch ip data
ips_data = asyncio.run(fetch_all_ips(ips))

# map
coord_data = [np.array(item['loc'].split(','), dtype=np.float64) for item in ips_data]

mymap = folium.Map(location=[20.0, 0.0], zoom_start=2, max_zoom=1)
folium.plugins.HeatMap(coord_data).add_to(mymap)
folium.TileLayer('cartodbdark_matter').add_to(mymap)

mymap.save('ip_heatmap.html')
