import os
import json
from argparse import ArgumentParser
from datetime import datetime
from utils.get_datasets import get_zh_dataset, get_en_dataset
from utils.text_process import process_zh, process_en

t = datetime.now().strftime('%Y-%m-%d')  # record the time now


def get_zh_date():
    p = os.path.join(args.save_path, f'zh_dataset_{args.hot_top_k}_{args.answer_top_k}_{t}.json')
    # print(p)
    try:
        with open(p, 'r', encoding='utf-8') as f:
            print(f'Find data file {p}')
            data = json.load(f)
    except FileNotFoundError as e:
        print(f'Cannot find {p}, create new data now.')
        data = get_zh_dataset(args.save_path, args.hot_top_k, args.answer_top_k)
    """TODO
    对json数据的处理，转换成纯文本
    """
    data = ...
    data_after_process = process_zh(data)
    return data_after_process


def main():
    zh_date = get_zh_date()
    # print(zh_data)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--save_path', type=str, default='saves')
    parser.add_argument('--hot_top_k', type=int, default=50)
    parser.add_argument('--answer_top_k', type=int, default=50)  # 20数据大概为1.6M
    args = parser.parse_args()

    print(args)

    main()
