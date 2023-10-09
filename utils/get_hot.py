"""This module obtain the top k urls of hot urls in zhihu

Please fill the cookie and user-agent to guarantee the validation of this module.

The final results will be saved at 'saves' as json

* Author: Yang Li
* Affiliation: Institute of Computing Technology, Chinese Academy of Sciences
"""

import os
import time

import requests
import json
from lxml import etree
from selenium import webdriver
from datetime import datetime

url_zhihu = 'https://www.zhihu.com/hot'
url_quora = 'https://www.quora.com/'

# change the following dict with yours
headers = {
    'cookie': '_zap=15f79d6c-9c4e-46c7-8bc2-a4f0768f5016; d_c0=APAXgWgo8haPTo7cOqPvwe5vD9Bac6zgM28=|1686988059; YD00517437729195%3AWM_TID=VsIup%2FbBi1BEUAQURBfRkPGVZx267%2FRl; YD00517437729195%3AWM_NI=jdQebo%2FDtOxPSJkdbQUfalSYcN%2Bx%2BE6lpdbYo0dG4yrohLDNR7feaSm51MetkP%2FnjCTsI2%2FYhsCEpu2rGAYZ5bXnyBo58SD49kY9kbcdn1DI8usIHLvgAM5qN1GDOuzwbHc%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6ee84b27c9598aa91f03ba6ac8ba3d44f828f8fb1d564a5bc9cb5d35a86b2ba9ae52af0fea7c3b92aaabc9f86e165ed9cbcb0fb5c9196a585e15b97baaf8dd253a192e599aa4ff6b4c085e153adf0aca8b773b2b1a8adc74692e9aa86e459afebffaee880a990e18fe94998ad87d3ae53acad8da6f37ff2ae89a2dc52f7be988ffc4aadebf8b4c740fbb597daea6aa1bca2d2c743fcabbdaacb48b6b98faeb87b8eef89a5ce7fbaa9aea9e237e2a3; q_c1=9a0632ce03434a1ba51b17387964e988|1690603870000|1690603870000; _xsrf=94d88be3-e63d-4d3f-b298-272accba9d8b; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1695285162,1695285543,1695474847,1696676802; z_c0=2|1:0|10:1696676802|4:z_c0|80:MS4xd0dKT0J3QUFBQUFtQUFBQVlBSlZUY0tKRG1ZaUZxV0x5NkE5SHU5UW9VQjBtSTUzMldzMDd3PT0=|911d26209e0a5902068ae654f43a12c707f18aed640438cb3bbeb7c088cd1000; SESSIONID=dgp67VoTzsR25we9dB0onhqyRzKlElfpqvuntkf0KlY; JOID=VVkVBULWXOFNGmI9PtcEf2V5S8cvtDqXdCMyU2yiKbJ5IBteBhNgySkSZTo3tekPvYZ5KoMzkkal5jWUuAblDBw=; osd=UFoSAkzTX-ZKFGc-OdAKemZ-TMkqtz2QeiYxVGusLLF-JxVbBRRnxywRYj05sOoIuoh8KYQ0nEOm4TKavQXiCxI=; tst=h; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1696676966; KLBRSID=f48cb29c5180c5b0d91ded2e70103232|1696677011|1696676321',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Connection': 'close'
}

headers_quora = {
    'cookie': 'm-b=ImwkWxBoXb2bpzIn4Pt5Og==; m-b_lax=ImwkWxBoXb2bpzIn4Pt5Og==; m-b_strict=ImwkWxBoXb2bpzIn4Pt5Og==; m-s=u_JhtA_rNNeUVuzyHImCEg==; m-theme=light; m-dynamicFontSize=regular; m-lat=A63zm3UMiphVU1j1wa19cA==; m-login=1; m-uid=2344827106; _gcl_au=1.1.1900167259.1696685660; _scid=2cc75deb-cc43-4d2c-aaca-9e2c2def8bcb; _scid_r=2cc75deb-cc43-4d2c-aaca-9e2c2def8bcb; _fbp=fb.1.1696685661869.1138928366; _sctr=1%7C1696608000000; __stripe_mid=b4aa6e10-34e9-415b-810e-4f7e534901e250f3be; _sc_cspv=https%3A%2F%2Ftr.snapchat.com%2Fp; m-sa=1; __stripe_sid=4323c8ee-b340-4182-8fc9-a82a1bb62531d3437e; __gads=ID=9d088131488b0295-226ea83f2fe30077:T=1696685830:RT=1696758977:S=ALNI_MYixouPi3iEfPBEiZimGn3FqUTiYg; __gpi=UID=000009ec8865870e:T=1696685830:RT=1696758977:S=ALNI_MYBoqa2FV5Cy6Led6SIlGzmR-Xoxw',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
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

    hot_list.clear()
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


def get_qa_infos_quora(num_q=top_k, usr_info=None):
    # 异步请求，需要使用selenuim模拟浏览器动作
    if usr_info is None:
        usr_info = headers_quora
    global top_k
    if num_q > 0 and num_q != top_k:
        top_k = num_q

    hot_list.clear()

    # 注意对应自己的chrome版本
    # 在chrome地址栏输入chrome://version即可查看当前chrome的版本。下载对应版本的chromedeiver
    driver = webdriver.Chrome(os.path.join('utils', 'chromedriver_win64', 'chromedriver.exe'))
    driver.get(url_quora)

    # 登录
    username = driver.find_element_by_xpath('//*[@id="email"]')
    username.send_keys('ly18093725295@gmail.com')
    password = driver.find_element_by_xpath('//*[@id="password"]')
    password.send_keys('Future520')
    submit = driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[4]/button')
    time.sleep(30)
    submit.click()

    # 获取问题和问题链接
    time.sleep(10)

    # 翻 top_k/2 页，保证足够多的问题纳入
    js = "window.scrollTo(0,document.body.scrollHeight)"
    for _ in range(int(top_k / 2)):
        driver.execute_script(js)
        time.sleep(3)

    questions_ele = driver.find_elements_by_xpath(
        '//div[@class="q-box dom_annotate_multifeed_bundle_AnswersBundle qu-borderAll qu-borderRadius--small qu-borderColor--raised qu-boxShadow--small qu-mb--small qu-bg--raised"]//span[@class="q-box qu-userSelect--text"]')
    # questions_ele = driver.find_elements_by_xpath('//span[@class="q-box qu-userSelect--text"]')

    for ele in questions_ele:
        try:
            ele.click()
            time.sleep(1)  # 防止被ban
        except:
            time.sleep(1)
            continue

    urls_ele = driver.find_elements_by_xpath(
        '//a[@class="q-box Link___StyledBox-t2xg9c-0 dFkjrQ puppeteer_test_link qu-display--block qu-cursor--pointer qu-hover--textDecoration--underline"]')
    urls = [x.get_attribute('href') for x in urls_ele]
    print(len(urls))
    # print(urls)

    # 只取top_k个
    for idx, item in enumerate(urls[:top_k], start=1):
        hot_info = {
            'title': item.split('/')[-1].replace('-', ' '),
            'time': t,
            'url': item,
        }
        # print(hot_info)

        hot_list.append({
            'idx': idx,
            'info': hot_info
        })

    save_to_json(prefix='quora')
    return hot_list
