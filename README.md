- Yang Li
- Institute of Computing Technology, Chinese Academy of Sciences

- 本仓库只作学习用途，请勿用于任何商业行为和违法行为，否则后果自负。

# 获取数据

## 知乎数据

可以直接使用`requests`库对网页进行get操作，将返回的html使用`lxml`库进行解析，得到问题及问题链接：

<img src="README.assets/image-20231007195727315.png" alt="image-20231007195727315" style="zoom:35%;" />

对问题的所有答案进行爬取时，使用知乎的api获得网页内容的json格式数据：

<img src="README.assets/image-20231009104554356.png" alt="image-20231009104554356" style="zoom:35%;" />

可以看到最后使用`is_end`和`next`指明了该页面是否需要翻页已经翻页后的页面地址，因此我们只需要针对一个问题访问多个url就可以得到全部的回答：

```python
global question_id
question_id = url.split('/')[-1]  # url为问题链接

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
```

对获得的数据进行简单的组织，并保存在json里即可。

同时，由于知乎热榜是变化的，每天爬取热榜内容大概在2M左右，因此扩展数据容量比较方便，只需要每天都爬就可以了。

## Quora数据

Quora是动态加载页面，因此我们只能通过`selenium`库对浏览器行为进行模拟。

<img src="README.assets/image-20231009103902324.png" alt="image-20231009103902324" style="zoom:35%;" />

单击`more`之后会得到问题的链接：

<img src="README.assets/image-20231009104012112.png" alt="image-20231009104012112" style="zoom:35%;" />

和知乎一样，Quora的首页也是实时变化的，因此扩展数据容量也比较方便。

滚动页面时注意如果已经到底端，就跳出循环：

```python
# 翻页，保证得到足够多的回答
js = "window.scrollTo(0,document.body.scrollHeight)"
temp_height = 0
for _ in range(int(top_k / 2)):
    driver.execute_script(js)
    time.sleep(3)
    # 获取当前滚动条距离顶部的距离
    check_height = driver.execute_script(
        "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
    # 如果两者相等说明到底了
    if check_height == temp_height:
        break
    temp_height = check_height
```

Quora的回答框也很有规律：

<img src="README.assets/image-20231009184532577.png" alt="image-20231009184532577" style="zoom:35%;" />

这时就需要xpath模糊匹配，获得所有包含`dom_annotate_question_answer_item_`的div元素：

```python
ans_block = driver.find_elements_by_xpath('//div[contains(@class, "dom_annotate_question_answer_item_")]')
```

然后依次**定位到元素位置**，再进行单击click，**确保回答被展开**，然后再获取回答内容：

```python
for block in ans_block:
    driver.execute_script("arguments[0].scrollIntoView();", block)  # 滚动到该位置
    time.sleep(1)
    block.click()  # 展开
    time.sleep(1)
```

<img src="README.assets/image-20231009185300875.png" alt="image-20231009185300875" style="zoom:35%;" />

需要注意几点：

1. 对空回答进行过滤，因为有些提问是照片或链接，回答里不一定有文字。

2. Quora存在匿名回答，可能无法正确爬取`usr_url`，注意做好判断。

3. 不要爬到"Related"

   ```python
   try:
       # 跳过Related
       related = block.find_element_by_xpath('.//div[@class="q-text qu-dynamicFontSize--small qu-fontWeight--regular"]').text
       if related == 'Related':
           continue
   except:
           pass
   ```

# 数据处理

## 中文数据

### 数据清洗

- 无用符号
- 特殊符号

```python
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
```

### 分词

使用`jieba`库进行分词

```python
import jieba

text = ''
word_list = jieba.cut(text)
```

## 英文数据

### 数据清洗 Cleaning

- 无用符号
- 特殊符号

```python
def clean_text(text):
    """清理数字、符号、特殊字符"""
    text = re.sub(r'\d+', '', text)  # 删除数字
    for c in string.punctuation:  # 删除英文符号
        text = text.replace(c, '')
    for c in zhon.hanzi.punctuation:  # 删除中文符号
        text = text.replace(c, '')
    text = re.sub(' +', ' ', text)  # 连续空格变为一个
    return text


def process_en(text):
    text = clean_text(text.strip().lower())
    text = re.sub('[\u4e00-\u9fa5]', '', text)  # 删除中文
    # 删除除英文字符和空格以外的所有非法字符，其实只保留以下这行就够了
    text = re.sub(r'[^A-Za-z ]+', '', text)
    return text
```

- 停用词，这里要十分注意，停用词不能用字符串的`replace`函数进行处理（否则会删除所有该字符串，而不是只删单词），只能判等再删除。

```python
stop_words = set(stopwords.words('english'))
for word in word_list:
    if mode == 'en' and word in stop_words:  # 删除停用词
        continue
```

**注意：考虑到与中文保持一致，因此最终并未去除停用词**

### 分词 Segmentation

英文相较中文而言分词会简单很多，使用空格进行分割即可，但是考虑到为了熟悉使用这些库和准确性，选择使用`nltk.tokenize`进行处理。

```python
from nltk.tokenize import word_tokenize

text = ''
word_list = word_tokenize(text)
```

### 标准化

使用`nltk`库进行处理，包含以下两个方面：

- 词干提取 Stemming，从单词中去除词缀并返回词根，返回的并不是单词，因此我们并不做词干提取，只做词形还原。
- 词形还原 Lemmazation

  ```python
  from nltk.tokenize import word_tokenize
  word_list = [wnl.lemmatize(word) for word in word_list]
  ```

# 计算文本熵

## 中文

## 英文

# 验证Zipf's law（齐夫定律）

在一个自然语言的语料库中，一个词的出现频数和这个词在这个语料中的排名（这个排名是基于出现次数的）成反比。

> Zipf's law states that given some corpus of natural language utterances, the frequency of any word is inversely
> proportional to its rank in the frequency table.

因此，我们可以以rank为自变量，freq为应变量，画出图像，如果图像是一条直线（反比例函数），则说明定律是正确的：

$$
\text{freq}=k\times\frac{1}{\text{rank}}
$$

数据越多，验证越准确，因此我们选择共做3次验证，每次增加一组爬取的数据。

## 词频统计

创建一个`Process`类用于接收数据并对其进行隐式的统计处理，防止在函数调用过程中更改原有数据，保证安全性和准确性：

```python
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
    def construct_and_process(cls, data_dict, mode):
        return cls(data_dict, mode)

    def process(self, data_dict):
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
    def calc_entropy(freq_dict):
        return ...

    @staticmethod
    def plot(freq_dict, save_path=None):
        ...

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
    def word_freq_dict(self):
        """返回按频率降序排序的 词-频率 字典"""
        return dict(sorted(self.__word_freq_dict.items(), key=lambda x: x[-1], reverse=True))

    @property
    def character_sum(self):
        """获取数据集中总字（符）数"""
        return np.sum(list(self.__char_freq_dict.values()))

    @property
    def character_freq_dict(self):
        """返回按频率降序排序的 字符-频率 字典"""
        return dict(sorted(self.__char_freq_dict.items(), key=lambda x: x[-1], reverse=True))
```

以上代码中使用的公共函数`process_zh`和`process_en`定义已在上文中给出，这三个函数接收字符串文本`text`
为参数，可以独立运行，并不依赖于我们的传入的json数据，因此并不将其作为类方法，而是单独作为一个module。

## 画图验证

# 参考文档

1. [python爬虫实战（2）——爬取知乎热榜内容 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/356993821)
2. [爬虫实战7：知乎热榜爬取 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/163854249)
3. [python爬虫系列--lxml（etree/parse/xpath)的使用_etree.parse-CSDN博客](https://blog.csdn.net/qq_35208583/article/details/89041912)
4. [Python 获取并输出当前日期、时间_python输出当前日期月日-CSDN博客](https://blog.csdn.net/beautiful77moon/article/details/88877519)
5. [【python】保存数据到JSON文件-CSDN博客](https://blog.csdn.net/lm3758/article/details/82966591)
6. [【2023知乎爬虫】知友怎么看待《罗刹海市》？爬了上千条知乎回答！ - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/647671891)
7. [Python爬虫实战：抓取知乎问题下所有回答-腾讯云开发者社区-腾讯云 (tencent.com)](https://cloud.tencent.com/developer/article/1881294)
8. [爬取quora中China相关的话题 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/292575811)
9. [selenium.common.exceptions.WebDriverException: Message: Service chromedriver unexpectedly exited.-CSDN博客](https://blog.csdn.net/qq_51459600/article/details/118497137)
10. [使用Python的Selenium进行网络自动化的入门教程 - 掘金 (juejin.cn)](https://juejin.cn/post/7171300716194054180)
11. [Python爬虫（1）一次性搞定Selenium(新版)8种find_element元素定位方式_find_element python-CSDN博客](https://blog.csdn.net/qq_16519957/article/details/128740502)
12. [如何使用Xpath定位元素（史上最清晰的讲解）_xpath选择某个内容的元素-CSDN博客](https://blog.csdn.net/qq_43022048/article/details/89455496?ops_request_misc=%7B%22request%5Fid%22%3A%22167487981916800213085071%22%2C%22scm%22%3A%2220140713.130102334.pc%5Fall.%22%7D&request_id=167487981916800213085071&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~hot_rank-5-89455496-null-null.142^v71^control_1,201^v4^add_ask&utm_term=XPATH定位&spm=1018.2226.3001.4187)
13. [xpath模糊定位的方法 - 简书 (jianshu.com)](https://www.jianshu.com/p/8e4370e68bc0)
14. [学爬虫利器XPath,看这一篇就够了 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/29436838)
15. [selenium框架中driver.close()和driver.quit()关闭浏览器-CSDN博客](https://blog.csdn.net/yangfengjueqi/article/details/84338167)
16. [Xpath 一些使用中遇到的情况 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/72452672)
17. [python+selenium 滚动条/内嵌滚动条循环下滑，判断是否滑到最底部_webdriver 滚动条多次向下-CSDN博客](https://blog.csdn.net/zhaoweiya/article/details/108996126)
18. [用Python正则实现词频统计并验证Zipf-Law_如何判断是否符合zipf's law python-CSDN博客](https://blog.csdn.net/weixin_43353612/article/details/105147148)
19. [NLP入门-- 文本预处理Pre-processing - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/53277723)
20. [Python 类的几个内置装饰器—— Staticmethod Classmethod Property-CSDN博客](https://blog.csdn.net/dzysunshine/article/details/106156920)
21. [Python collections模块之defaultdict()详解_from collections import defaultdict-CSDN博客](https://blog.csdn.net/chl183/article/details/107446836)
22. [NLTK使用方法总结_nltk.tokenize-CSDN博客](https://blog.csdn.net/asialee_bird/article/details/85936784)
23. [@classmethod使得类里面的某个方法可以直接调用类的方法和变量_classmethod内调用类方法入参-CSDN博客](https://blog.csdn.net/qq_41000421/article/details/84955525)
24. [(1 封私信 / 21 条消息) python中的cls到底指的是什么，与self有什么区别? - 知乎 (zhihu.com)](https://www.zhihu.com/question/49660420)
25. [数据分析培训 | Python文本预处理：步骤、使用工具及示例 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/55962828)
26. [python | 字符串去除(中文、英文、数字、标点符号)_点号教程免费代码_买猫咪的小鱼干的博客-CSDN博客](https://blog.csdn.net/weixin_43360896/article/details/114499028)
27. [Python删除字符串中的符号_python去除字符串中的符号_O_nice的博客-CSDN博客](https://blog.csdn.net/O_nice/article/details/124043331)
28. [python - 如何只保留字母数字和空格，同时忽略非 ASCII？ - IT工具网 (coder.work)](https://www.coder.work/article/3189266)