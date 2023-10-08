"""This module obtain the top k urls of hot urls in zhihu

Please fill the cookie and user-agent to guarantee the validation of this module.

The final results will be saved at 'saves' as json

* Author: Yang Li
* Affiliation: Institute of Computing Technology, Chinese Academy of Sciences
"""

import os
import requests
import json
from lxml import etree
from datetime import datetime

url_zhihu = 'https://www.zhihu.com/hot'

# change the following dict with yours
headers = {
    'cookie': '_zap=15f79d6c-9c4e-46c7-8bc2-a4f0768f5016; d_c0=APAXgWgo8haPTo7cOqPvwe5vD9Bac6zgM28=|1686988059; YD00517437729195%3AWM_TID=VsIup%2FbBi1BEUAQURBfRkPGVZx267%2FRl; YD00517437729195%3AWM_NI=jdQebo%2FDtOxPSJkdbQUfalSYcN%2Bx%2BE6lpdbYo0dG4yrohLDNR7feaSm51MetkP%2FnjCTsI2%2FYhsCEpu2rGAYZ5bXnyBo58SD49kY9kbcdn1DI8usIHLvgAM5qN1GDOuzwbHc%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6ee84b27c9598aa91f03ba6ac8ba3d44f828f8fb1d564a5bc9cb5d35a86b2ba9ae52af0fea7c3b92aaabc9f86e165ed9cbcb0fb5c9196a585e15b97baaf8dd253a192e599aa4ff6b4c085e153adf0aca8b773b2b1a8adc74692e9aa86e459afebffaee880a990e18fe94998ad87d3ae53acad8da6f37ff2ae89a2dc52f7be988ffc4aadebf8b4c740fbb597daea6aa1bca2d2c743fcabbdaacb48b6b98faeb87b8eef89a5ce7fbaa9aea9e237e2a3; q_c1=9a0632ce03434a1ba51b17387964e988|1690603870000|1690603870000; _xsrf=94d88be3-e63d-4d3f-b298-272accba9d8b; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1695285162,1695285543,1695474847,1696676802; z_c0=2|1:0|10:1696676802|4:z_c0|80:MS4xd0dKT0J3QUFBQUFtQUFBQVlBSlZUY0tKRG1ZaUZxV0x5NkE5SHU5UW9VQjBtSTUzMldzMDd3PT0=|911d26209e0a5902068ae654f43a12c707f18aed640438cb3bbeb7c088cd1000; SESSIONID=dgp67VoTzsR25we9dB0onhqyRzKlElfpqvuntkf0KlY; JOID=VVkVBULWXOFNGmI9PtcEf2V5S8cvtDqXdCMyU2yiKbJ5IBteBhNgySkSZTo3tekPvYZ5KoMzkkal5jWUuAblDBw=; osd=UFoSAkzTX-ZKFGc-OdAKemZ-TMkqtz2QeiYxVGusLLF-JxVbBRRnxywRYj05sOoIuoh8KYQ0nEOm4TKavQXiCxI=; tst=h; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1696676966; KLBRSID=f48cb29c5180c5b0d91ded2e70103232|1696677011|1696676321',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Connection': 'close'
}

# change the following variable to control the number of urls
top_k = 50

# the final ret list and path
save_path = 'saves'
hot_list = []

t = datetime.now().strftime('%Y-%m-%d')  # record the time now


def save_to_json(path=None, prefix=None):
    if prefix not in ['zhihu', 'quora']:
        raise KeyError(f'prefix must be either zhihu or quora, not {prefix}.')
    if path is None or os.path.exists(path) is False:
        path = save_path
    # print(hot_dict)
    with open(os.path.join(path, f'{t}_{prefix}_top{top_k}_hot-news_infos.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(hot_list, indent=2, ensure_ascii=False))  # indent控制缩进，ensure_ascii的值设为False以正常显示中文


def get_hot_infos_zhihu(num_news=top_k, usr_info=None):
    if usr_info is None:
        usr_info = headers
    global top_k
    if num_news > 0 and num_news != top_k:
        top_k = num_news

    response = requests.get(url_zhihu, headers=usr_info)
    text = response.text
    html_correct = etree.HTML(text)  # 构造一个XPath解析对象并对HTML文本进行自动修正
    hot_items = html_correct.xpath("//section[@class='HotItem']")  # 选取所有section子元素，不管位置

    for item in hot_items[:top_k]:
        try:
            rank = item.xpath("./div[@class='HotItem-index']//text()")[0]  # 热榜排名
            title = item.xpath(".//div[@class='HotItem-content']/a/@title")[0]  # 标题
            href = item.xpath(".//div[@class='HotItem-content']/a/@href")[0]  # 链接

            metrics = item.xpath(".//div[@class='HotItem-metrics HotItem-metrics--bottom']/text()")  # 热度，用于过滤广告
            if '广告' in [x.strip() for x in metrics]:
                raise KeyError('Pass the advertisement.')

            hot_info = {
                'title': title,
                'time': t,
                'url': href,
            }
            # print(hot_info)

            hot_list.append({
                'idx': int(rank),
                'info': hot_info
            })
        except:
            pass

    save_to_json(prefix='zhihu')
    return hot_list
