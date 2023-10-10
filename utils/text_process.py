import re
import jieba
import nltk
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict

nltk.download()


def clean_text(text):
    """清理数字、符号、特殊字符"""
    return text


def process_zh(text):
    text = clean_text(text.strip())
    """TODO
    清理非中文字符
    """
    return text


def process_en(text):
    text = clean_text(text.strip().lower())
    stop_words = set(stopwords.words('english'))
    """TODO
    清理停用词和非英文字符
    """
    return text


class Process:
    def __init__(self, data_dict, mode):
        self.__data_dict = data_dict
        if mode not in ['zh', 'en']:
            raise KeyError(f'mode should be either zh or en, not {mode}')
        self.__mode = mode

        self.__pure_ans_list = []
        self.__word_freq_dict = defaultdict(int)
        self.__char_freq_dict = defaultdict(int)
        self._process()

    def _process(self):
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
            self.__word_freq_dict[word] += 1
            for c in word:
                self.__char_freq_dict[c] += 1

    @property
    def question_answer_dict(self):
        """获取传入的 问题-答案 字典"""
        return self.__data_dict

    @property
    def pure_answer_list(self):
        """获取处理过后的所有回答"""
        return self.__pure_ans_list

    @property
    def answer_num(self):
        """获取数据集中回答的个数"""
        return len(self.__pure_ans_list)

    @property
    def answer_average_len(self):
        """获取数据集中回答的平均字符长度"""
        return self.character_sum / len(self.__pure_ans_list)

    @property
    def word_sum(self):
        """获取数据集总词数"""
        return np.sum(list(self.__word_freq_dict.values()))

    @property
    def character_sum(self):
        """获取数据集中总字（符）数"""
        return np.sum(list(self.__char_freq_dict.values()))
