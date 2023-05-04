import pickle

from tqdm import tqdm
from transformers import AutoTokenizer

a = pickle.load(open("tokenize_saved/select_non_pinyin.pkl", "rb"))
print("导入pkl成功")

vocabulary = {char for i in a for char in i[0]}
vocabulary.add("<\w>")
print("初始化词表成功")

word_list_freq = [i[1] for i in a]
sub_words_list = [[char for char in i[0]] + ["<\w>"] for i in a]
print("初始化sub_words成功")

pair_freq = {(sub_words[i], sub_words[i + 1]): 0 for sub_words in sub_words_list for i in range(len(sub_words) - 1)}
for index, sub_words in tqdm(enumerate(sub_words_list)):
    for i in range(len(sub_words) - 1):
        pair_freq[(sub_words[i], sub_words[i + 1])] += word_list_freq[index]
print("初始化pair_freq成功")

step_num = 15000
merge_rules = []
for step in tqdm(range(step_num)):
    pair = max(pair_freq, key=pair_freq.get)
    freq = pair_freq[pair]
    merge_rules.append(pair)
    vocabulary.add(pair[0] + pair[1])

    for index, sub_words in enumerate(sub_words_list):
        i = 0
        count = 0
        flag = False
        while i < len(sub_words) - 1:
            if (sub_words[i], sub_words[i + 1]) == pair:
                if flag == False:
                    flag = True
                    for j in range(len(sub_words) - 1):
                        pair_freq[(sub_words[j], sub_words[j + 1])] -= word_list_freq[index]
                        if pair_freq[(sub_words[j], sub_words[j + 1])] == 0:
                            pair_freq.pop((sub_words[j], sub_words[j + 1]))
                sub_words[i] = sub_words[i] + sub_words[i + 1]
                sub_words.pop(i + 1)
                count += 1
            i += 1
        if flag:
            for j in range(len(sub_words) - 1):
                pair_freq[(sub_words[j], sub_words[j + 1])] = pair_freq.get((sub_words[j], sub_words[j + 1]), 0) + word_list_freq[index]
        if count == freq:
            break

    if step == 0 or (5000 <= step < 10000 and step % 1000 == 0) or (step >= 10000 and step % 250 == 0):
        with open(f"tokenize_result/vocabulary{step}.txt", "w", encoding="UTF-8") as f:
            f.write("\n".join(sorted(list(vocabulary))))
        with open(f"tokenize_result/merge_rules{step}.txt", "w", encoding="UTF-8") as f:
            f.write("\n".join([rule[0] + " " + rule[1] for rule in merge_rules]))
