import collections
import json
import os
import pickle
import re
import threading

# 检查中文
# zh_pattern = re.compile(u'[\u4e00-\u9fa5]')
# 检查非中文
# zh_pattern = re.compile(u'[^\u4e00-\u9fa5]+')

thread_num = 20
zh_pattern = re.compile(u'[^\u4e00-\u9fa5]+')
totals = [{}] * thread_num
files = os.listdir("./data")
part_num = len(files) / thread_num


def one_thread(part_files, index):
    total = {}
    for file in part_files:
        raw = json.load(open("./data/" + file, "r", encoding="UTF-8"))
        texts = [i["content"] for i in raw]
        non_pinyin = []
        for text in texts:
            non_pinyin.extend(zh_pattern.findall(text))
        s = collections.Counter(non_pinyin)

        for key, value in s.items():
            total[key] = total.get(key, 0) + value
        print(file + "处理完成")
    totals[index] = total


thread_list = []
for i in range(thread_num):
    t = threading.Thread(target=one_thread, args=(files[int(part_num * i):int(part_num * (i + 1))], i))
    thread_list.append(t)

for t in thread_list:
    t.start()

for t in thread_list:
    t.join()

last = {}
for s in totals:
    for key, value in s.items():
        last[key] = last.get(key, 0) + value
pickle.dump(last, open("tokenize_saved/non_pinyin.pkl", "wb"))

# old = pickle.load(open("tokenize_saved/non_pinyin.pkl", "rb"))
#
# tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
#
# new = {}
#
# for key, value in tqdm(old.items()):
#     pre_tokenization = tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str(key)
#     for new_key, offset in pre_tokenization:
#         new[new_key] = new.get(new_key, 0) + value
#
# pickle.dump(new, open("tokenize_saved/clean_non_pinyin.pkl", "wb"))



# a = pickle.load(open("tokenize_saved/clean_non_pinyin.pkl", "rb"))
# t1 = sum(a.values())
# b = sorted(a.items(), key=lambda s: s[1], reverse=True)[:100000]
# t2 = sum([i[1] for i in b])
# print(t2 / t1)
# pickle.dump(b, open("tokenize_saved/select_non_pinyin.pkl", "wb"))

