import os
import json
from datetime import datetime
from .get_hot import get_hot_infos_zhihu, get_qa_infos_quora
from .get_content import get_answer_content_zhihu, get_answer_content_quora

t = datetime.now().strftime('%Y-%m-%d')  # record the time now


def get_zh_dataset(save_path, hot_top_k, answer_top_k, date_time=None):
    date_time = t if date_time is None else date_time
    try:
        hot_urls_path = os.path.join(save_path, f'{date_time}_zhihu_top{hot_top_k}_hot-news_infos.json')
        with open(hot_urls_path, 'r', encoding='utf-8') as f:
            hot_urls = json.load(f)
    except FileNotFoundError as e:
        print(f'Cannot find the hot news at {date_time}, create new data today.')
        date_time = t
        hot_urls = get_hot_infos_zhihu(hot_top_k)
    # print(hot_urls)

    content_list = []
    for item_dict in hot_urls:
        url = item_dict['info']['url']
        question_id = url.split('/')[-1]

        print(f'begin processing hot news {item_dict["idx"]} id-{question_id}')

        answers_dict = get_answer_content_zhihu(url, num_ans=answer_top_k, date_time=date_time)[0]
        answers_dict_simple = {
            key: val['content'] for key, val in answers_dict.items()
        }
        data = {
            'question_id': question_id,
            'title': item_dict['info']['title'],
            'answers': answers_dict_simple
        }

        content_list.append(data)

    with open(os.path.join(save_path, f'zh_dataset_{hot_top_k}_{answer_top_k}_{date_time}.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(content_list, indent=2, ensure_ascii=False))

    return content_list


def get_en_dataset(save_path, hot_top_k, answer_top_k, date_time=None):
    date_time = t if date_time is None else date_time
    try:
        hot_urls_path = os.path.join(save_path, f'{date_time}_quora_top{hot_top_k}_hot-news_infos.json')
        with open(hot_urls_path, 'r', encoding='utf-8') as f:
            hot_urls = json.load(f)
    except FileNotFoundError as e:
        print(f'Cannot find the hot news at {date_time}, create new data today.')
        date_time = t
        hot_urls = get_qa_infos_quora(hot_top_k)
    # print(hot_urls)

    content_list = []
    for item_dict in hot_urls[:1]:
        url = item_dict['info']['url']
        answers_dict = get_answer_content_quora(url, answer_top_k, date_time)

        answers_dict_simple = {
            key: val['content'] for key, val in answers_dict.items()
        }
        data = {
            'question_id': url,
            'title': item_dict['info']['title'],
            'answers': answers_dict_simple
        }

        content_list.append(data)

    with open(os.path.join(save_path, f'en_dataset_{hot_top_k}_{answer_top_k}_{date_time}.json'), 'w',
              encoding='utf-8') as f:
        f.write(json.dumps(content_list, indent=2, ensure_ascii=False))

    return content_list
