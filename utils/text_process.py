from __future__ import annotations

import re
import string
from collections import defaultdict
from math import log2

import jieba
import matplotlib.pyplot as plt
import numpy as np
import zhon
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def clean_text(text):
    """清理数字、符号、特殊字符"""
    text = re.sub(r'\d+', '', text)  # 删除数字
    for c in string.punctuation:  # 删除英文符号
        text = text.replace(c, '')
    for c in zhon.hanzi.punctuation:  # 删除中文符号
        text = text.replace(c, '')
    text = re.sub(' +', ' ', text)  # 连续空格变为一个
    return text


def process_zh(text):
    text = clean_text(text.strip())
    text = re.sub('[a-zA-Z]', '', text)  # 删除英文
    # 删除除中文和空格以外的所有非法字符，其实只保留以下这行就够了
    text = re.sub('([^\u4e00-\u9fa5 ])', '', text)
    return text


def process_en(text):
    text = clean_text(text.strip().lower())
    text = re.sub('[\u4e00-\u9fa5]', '', text)  # 删除中文
    # 删除除英文字符和空格以外的所有非法字符，其实只保留以下这行就够了
    text = re.sub(r'[^A-Za-z ]+', '', text)
    return text


class Process:
    def __init__(self, data_dict, mode):
        self.__data_dict = data_dict
        if mode not in ['zh', 'en']:
            raise KeyError(f'mode should be either zh or en, not {mode}')
        self.__mode = mode

        self.__stop_words = set(stopwords.words('english'))

        self.__pure_ans_list = []
        self.__word_freq_dict = defaultdict(int)
        self.__char_freq_dict = defaultdict(int)
        self._process()

    @classmethod
    def construct_and_process(cls, data_dict: list[dict], mode: str) -> Process:
        return cls(data_dict, mode)

    def process(self, data_dict: list[dict]) -> None:
        self.__data_dict = data_dict
        self._process()

    def _process(self):
        self.__pure_ans_list.clear()
        self.__word_freq_dict.clear()
        self.__char_freq_dict.clear()
        for item in self.__data_dict:
            if not item['answers']:  # 未获取到任何答案
                continue
            for ans_text in iter(item['answers'].values()):
                if self.__mode == 'zh':
                    pure_text = process_zh(ans_text)
                    word_list = jieba.cut(pure_text)
                else:
                    pure_text = process_en(ans_text)
                    wnl = WordNetLemmatizer()
                    word_list = [wnl.lemmatize(word) for word in word_tokenize(pure_text)]

                self._update_freq_dict(word_list)
                self.__pure_ans_list.append(pure_text)

    def _update_freq_dict(self, word_list):
        for word in word_list:
            if word == ' ':
                continue
            # if self.__mode == 'en' and word in self.__stop_words:  # 删除停用词
            #     continue
            self.__word_freq_dict[word] += 1
            for c in word:
                self.__char_freq_dict[c] += 1

    @staticmethod
    def calc_entropy(freq_dict: dict) -> float:
        entropy = 0.0
        char_sum = np.sum(list(freq_dict.values()))
        for k, v in freq_dict.items():
            prob = v / char_sum
            entropy -= prob * log2(prob)
        return entropy

    @staticmethod
    def plot(freq_dict: dict, top_k: int = 10000, save_path=None) -> None:
        save_path = '.' if save_path is None else save_path

        plt.title('Zipf-Law', fontsize=18)  # 标题
        plt.xlabel('rank', fontsize=18)  # 排名
        plt.ylabel('freq', fontsize=18)  # 频度

        plt.yticks([pow(10, i) for i in range(0, 4)])  # 设置y刻度
        plt.xticks([pow(10, i) for i in range(0, 4)])  # 设置x刻度

        plt.yscale('log')  # 设置纵坐标的缩放
        plt.xscale('log')  # 设置横坐标的缩放

        y = list(freq_dict.values())[:top_k]
        x = list(range(1, top_k + 1))
        plt.plot(x, y, 'b')  # 绘图
        plt.savefig(save_path)  # 保存图片

        plt.show()

    @property
    def question_answer_dict(self) -> defaultdict:
        """获取传入的 问题-答案 字典"""
        return self.__data_dict

    @property
    def pure_answer_list(self) -> list[str]:
        """获取处理过后的所有回答"""
        return self.__pure_ans_list

    @property
    def answer_num(self) -> int:
        """获取数据集中回答的个数"""
        return len(self.__pure_ans_list)

    @property
    def answer_average_len(self) -> float:
        """获取数据集中回答的平均字符长度"""
        return self.character_sum / len(self.__pure_ans_list)

    @property
    def word_sum(self) -> int:
        """获取数据集总词数"""
        return np.sum(list(self.__word_freq_dict.values()))

    @property
    def word_freq_dict(self) -> dict:
        """返回按频率降序排序的 词-频率 字典"""
        return dict(sorted(self.__word_freq_dict.items(), key=lambda x: x[-1], reverse=True))

    @property
    def character_sum(self) -> int:
        """获取数据集中总字（符）数"""
        return np.sum(list(self.__char_freq_dict.values()))

    @property
    def character_freq_dict(self) -> dict:
        """返回按频率降序排序的 字符-频率 字典"""
        return dict(sorted(self.__char_freq_dict.items(), key=lambda x: x[-1], reverse=True))
