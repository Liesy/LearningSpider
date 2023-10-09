"""This module obtain the top k contents of one hot url in zhihu

Please fill the cookie and user-agent to guarantee the validation of this module.

The final results will be saved at 'saves/[zhihu, quora]' as json

* Author: Yang Li
* Affiliation: Institute of Computing Technology, Chinese Academy of Sciences
"""

import os
import requests
import json
import time
from lxml import etree
from datetime import datetime
from selenium import webdriver

# change the following dict with yours
headers = {
    'cookie': '_zap=15f79d6c-9c4e-46c7-8bc2-a4f0768f5016; d_c0=APAXgWgo8haPTo7cOqPvwe5vD9Bac6zgM28=|1686988059; YD00517437729195%3AWM_TID=VsIup%2FbBi1BEUAQURBfRkPGVZx267%2FRl; YD00517437729195%3AWM_NI=jdQebo%2FDtOxPSJkdbQUfalSYcN%2Bx%2BE6lpdbYo0dG4yrohLDNR7feaSm51MetkP%2FnjCTsI2%2FYhsCEpu2rGAYZ5bXnyBo58SD49kY9kbcdn1DI8usIHLvgAM5qN1GDOuzwbHc%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6ee84b27c9598aa91f03ba6ac8ba3d44f828f8fb1d564a5bc9cb5d35a86b2ba9ae52af0fea7c3b92aaabc9f86e165ed9cbcb0fb5c9196a585e15b97baaf8dd253a192e599aa4ff6b4c085e153adf0aca8b773b2b1a8adc74692e9aa86e459afebffaee880a990e18fe94998ad87d3ae53acad8da6f37ff2ae89a2dc52f7be988ffc4aadebf8b4c740fbb597daea6aa1bca2d2c743fcabbdaacb48b6b98faeb87b8eef89a5ce7fbaa9aea9e237e2a3; q_c1=9a0632ce03434a1ba51b17387964e988|1690603870000|1690603870000; _xsrf=94d88be3-e63d-4d3f-b298-272accba9d8b; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1695285162,1695285543,1695474847,1696676802; z_c0=2|1:0|10:1696676802|4:z_c0|80:MS4xd0dKT0J3QUFBQUFtQUFBQVlBSlZUY0tKRG1ZaUZxV0x5NkE5SHU5UW9VQjBtSTUzMldzMDd3PT0=|911d26209e0a5902068ae654f43a12c707f18aed640438cb3bbeb7c088cd1000; SESSIONID=dgp67VoTzsR25we9dB0onhqyRzKlElfpqvuntkf0KlY; JOID=VVkVBULWXOFNGmI9PtcEf2V5S8cvtDqXdCMyU2yiKbJ5IBteBhNgySkSZTo3tekPvYZ5KoMzkkal5jWUuAblDBw=; osd=UFoSAkzTX-ZKFGc-OdAKemZ-TMkqtz2QeiYxVGusLLF-JxVbBRRnxywRYj05sOoIuoh8KYQ0nEOm4TKavQXiCxI=; tst=h; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1696676966; KLBRSID=f48cb29c5180c5b0d91ded2e70103232|1696677011|1696676321',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Connection': 'close'
}

# change the following variable to control the number of answers
top_k = 20

# the final ret list and path
save_path = 'saves'
answer_list = []
question_id = None  # 获取内容时更新

t = datetime.now().strftime('%Y-%m-%d')  # record the time now


def save_to_json(path=None, prefix=None, date_time=None):
    if prefix not in ['zhihu', 'quora']:
        raise KeyError(f'prefix must be either zhihu or quora, not {prefix}.')
    if path is None or os.path.exists(path) is False:
        path = save_path
    # print(hot_dict)

    p = os.path.join(path, prefix, f'top{top_k}', date_time)
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, f'answers_for_{question_id}.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(answer_list, indent=2, ensure_ascii=False))  # indent控制缩进，ensure_ascii的值设为False以正常显示中文


def spider_for_zhihu(url_api, ret_dict, offset=0, usr_info=None):
    if usr_info is None:
        usr_info = headers
    try:
        response = requests.get(url_api, headers=usr_info)
        text = response.text
        # print(text)

        # 处理爬取的数据（转换成json格式）
        text_json = json.loads(text)
        # print(text_json)
        if text_json['data'] is None:
            raise KeyError(f'web of question {question_id} is empty, please check it.')
        for idx, answer in enumerate(text_json['data'], start=1):
            author = answer['target']['author']['name']
            content = etree.HTML(answer['target']['content']).xpath('//*/text()')
            link = answer['target']['url']

            ret_dict[idx + offset] = {
                'author': author,
                'content': ''.join(content),
                'url': link
            }

        # 返回下页的5个回答
        # time.sleep(5)
        return text_json['paging']['is_end'], text_json['paging']['next']

    except:
        print(f'Fail to process: {url_api}')
        return True, None


def get_answer_content_zhihu(url: str, num_ans=top_k, usr_info=None, date_time=None):
    answer_list.clear()  # 否则会重复添加（因为都在内存里指向同一个空间）

    date_time = t if date_time is None else date_time

    global top_k
    if num_ans > 0 and num_ans != top_k:
        top_k = num_ans

    global question_id
    question_id = url.split('/')[-1]

    # 使用知乎的api进行爬取
    answer_dict = {}
    url_api = f'https://www.zhihu.com/api/v4/questions/{question_id}/feeds?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Creaction_instruction%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cvip_info%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&offset=0&limit=5&order=default&platform=desktop'
    is_end = False  # 不一定够20个回答，需要用该参数进行判断，防止死循环（也是知乎的api）
    # print(url_api)

    num_answer = len(answer_dict)
    while not is_end and num_answer < top_k:
        is_end, next_url_api = spider_for_zhihu(url_api, answer_dict, num_answer, usr_info)
        # print(type(is_end))
        num_answer = len(answer_dict)
        url_api = next_url_api

    answer_list.append(answer_dict)
    save_to_json(prefix='zhihu', date_time=date_time)
    return answer_list


def get_answer_content_quora(url, num_ans=top_k, date_time=None):
    answer_list.clear()  # 否则会重复添加（因为都在内存里指向同一个空间）
    date_time = t if date_time is None else date_time
    global top_k
    if num_ans > 0 and num_ans != top_k:
        top_k = num_ans

    # 注意对应自己的chrome版本
    # 在chrome地址栏输入chrome://version即可查看当前chrome的版本。下载对应版本的chromedeiver
    driver = webdriver.Chrome(os.path.join('utils', 'chromedriver_win64', 'chromedriver.exe'))
    driver.get(url)

    # 登录
    username = driver.find_element_by_xpath('//*[@id="email"]')
    username.send_keys('')
    password = driver.find_element_by_xpath('//*[@id="password"]')
    password.send_keys('')
    submit = driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[4]/button')
    time.sleep(30)
    submit.click()

    time.sleep(10)
    # 翻页，保证得到足够多的回答
    js = "window.scrollTo(0,document.body.scrollHeight)"
    for _ in range(int(top_k / 2)):
        driver.execute_script(js)
        time.sleep(3)

    # 将折叠的回答展开
    stack_ele = driver.find_elements_by_xpath('//div[@class="q-box qu-cursor--pointer QTextTruncated___StyledBox-sc-1pev100-0 gCXnis"]')
    for ele in stack_ele:
        try:
            ele.click()
            time.sleep(1)
        except:
            time.sleep(1)
            continue

    answer_dict = {}
    # 找到所有回答框
    ans_block = driver.find_elements_by_xpath('//div[@class="q-box dom_annotate_question_answer_item_0 qu-borderAll qu-borderRadius--small qu-borderColor--raised qu-boxShadow--small qu-mb--small qu-bg--raised"]')
    for idx,block in enumerate(ans_block[:num_ans], start=1):
        usr_url = block.find_element_by_xpath('//a[@class="q-box Link___StyledBox-t2xg9c-0 dFkjrQ puppeteer_test_link qu-color--gray_dark qu-cursor--pointer qu-hover--textDecoration--underline"]').get_attribute('href')
        answer = block.find_element_by_xpath('//span[@class="q-box qu-userSelect--text"]').text
        answer_dict[idx] = {
            'author': usr_url,
            'content': answer
        }

    answer_list.append(answer_dict)
    save_to_json(prefix='quora', date_time=date_time)
    return answer_list
