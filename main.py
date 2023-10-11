import os
import json
from argparse import ArgumentParser
from datetime import datetime
from glob import glob
from utils.get_datasets import get_zh_dataset, get_en_dataset
from utils.text_process import Process

t = datetime.now().strftime('%Y-%m-%d')  # record the time now


def get_data(mode, date_time=None):
    date_time = t if date_time is None else date_time

    if mode not in ['zh', 'en']:
        raise KeyError(f'mode should be either zh or en, not {mode}')
    p = os.path.join(args.save_path, f'{mode}_dataset_{args.hot_top_k}_{args.answer_top_k}_{date_time}.json')
    # print(p)
    try:
        with open(p, 'r', encoding='utf-8') as f:
            print(f'Find data file {p}')
            data = json.load(f)
    except FileNotFoundError as e:
        print(f'Cannot find {p}, create new data now.')
        if mode == 'zh':
            data = get_zh_dataset(args.save_path, args.hot_top_k, args.answer_top_k, date_time)
        else:
            data = get_en_dataset(args.save_path, args.hot_top_k, args.answer_top_k, date_time)
    return data


def get_data_from_answer_json(prefix):
    if prefix not in ['zhihu', 'quora']:
        raise KeyError(f'prefix must be either zhihu or quora, not {prefix}.')
    dir_path = os.path.join(args.save_path, prefix, args.hot_top_k, args.time)
    file_list = glob(os.path.join(dir_path, '*.json'))
    if not file_list:
        raise FileNotFoundError('No files.')
    content_list = []
    for idx, file_path in enumerate(file_list, start=1):
        with open(file_path, 'r', encoding='utf-8') as f:
            ans_dict = json.load(f)[0]
        answers_dict_simple = {
            key: val['content'] for key, val in ans_dict.items()
        }
        content_list.append({
            'question_id': idx,
            'title': '',
            'answers': answers_dict_simple
        })
    return content_list


def get_data_by_dates(mode, date_list=None):
    if date_list is None:
        print('Select all datasets.')
        file_list = glob(os.path.join(args.save_path, f'{mode}_dataset_{args.hot_top_k}_{args.answer_top_k}_*.json'))
    elif not date_list:
        raise FileNotFoundError('date list is empty.')
    else:
        file_list = [
            os.path.join(
                args.save_path,
                f'{mode}_dataset_{args.hot_top_k}_{args.answer_top_k}_{date}.json',
            )
            for date in date_list
        ]
    data = []
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            data_temp = json.load(f)
        data.extend(data_temp)
    return data


def main():
    en_data = get_data('en', args.time)
    zh_data = get_data('zh', args.time)
    # en_data = get_data_by_dates('en')
    # zh_data = get_data_by_dates('zh')

    en_after_processing = Process.construct_and_process(en_data, 'en')
    zh_after_processing = Process.construct_and_process(zh_data, 'zh')

    with open(os.path.join(args.save_path, 'en_word_freq.csv'), 'w', encoding='utf-8') as f:
        for k, v in en_after_processing.word_freq_dict.items():
            f.write(f'{k},{v}\n')
    with open(os.path.join(args.save_path, 'zh_word_freq.csv'), 'w', encoding='utf-8') as f:
        for k, v in zh_after_processing.word_freq_dict.items():
            f.write(f'{k},{v}\n')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--save_path', type=str, default='saves')
    parser.add_argument('--hot_top_k', type=int, default=50)
    parser.add_argument('--answer_top_k', type=int, default=50)  # 20数据大概为1.6M
    parser.add_argument('--time', type=str, default=None)
    args = parser.parse_args()

    print(args)

    main()
