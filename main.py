import json
import pickle
import threading
import time
import collections

from pypinyin import pinyin, Style
from tqdm import tqdm
from transformers import AutoTokenizer

additional_special_token = {}
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
tokenizer.add_tokens(["App"])


def get_vocabulary(py_char_list, py_freq_list):
    vocabulary = {char: 0 for py in py_char_list for char in py}
    for i in range(len(py_char_list)):
        for j in range(len(py_char_list[i])):
            vocabulary[py_char_list[i][j]] += py_freq_list[i]
    print(len(vocabulary))
    return vocabulary


def process(filepath):
    # texts = json.load(open(filepath, "r", encoding="UTF-8"))[:3000]
    # temp_list = [i[0] for item in tqdm(texts) for i in pinyin(item["content"], style=Style.TONE3, errors=lambda x: str(x))]
    # pickle.dump(temp_list, open("./temp.pkl", "wb"))
    temp_list = pickle.load(open("./temp.pkl", "rb"))

    py_freq_list = []
    py_char_list = []
    for py, freq in collections.Counter(temp_list).items():
        py_freq_list.append(freq)
        py_char_list.append([char for char in py])
        # if len(py) > 1:
        #     py_char_list[-1].append("<\w>")  # 说不定拼音后面的数字也可以充当这个角色

    a = time.time()
    step_num = 8000
    for step in range(step_num):
        pair_freq = {(py[i], py[i + 1]): 0 for py in py_char_list for i in range(len(py) - 1)}
        if len(pair_freq) == 0 or step == step_num - 1:
            vocabulary = get_vocabulary(py_char_list, py_freq_list)
            with open("./vocabulary.txt", "w", encoding="UTF-8") as f:
                f.write("\n".join([token.ljust(12, " ") + str(freq) for token, freq in vocabulary.items()]))
            return
        for i in range(len(py_char_list)):
            for j in range(len(py_char_list[i]) - 1):
                pair_freq[(py_char_list[i][j], py_char_list[i][j + 1])] += py_freq_list[i]
        pair = max(pair_freq, key=pair_freq.get)
        freq = pair_freq[pair]

        if freq == 1:
            vocabulary = get_vocabulary(py_char_list, py_freq_list)
            with open("./vocabulary.txt", "w", encoding="UTF-8") as f:
                f.write("\n".join([token.ljust(12, " ") + str(freq) for token, freq in vocabulary.items()]))
            return

        for py in py_char_list:
            i = 0
            count = 0
            while i < len(py) - 1:
                if (py[i], py[i + 1]) == pair:
                    py[i] = py[i] + py[i + 1]
                    py.pop(i + 1)
                    count += 1
                i += 1
            if count == freq:
                break

        if step % 100 == 0:
            get_vocabulary(py_char_list, py_freq_list)
            print(time.time() - a, freq)
            a = time.time()


process("./data/test.json")
