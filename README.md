# 整体规划
基于悟道数据集开源部分（200G）构建基于拼音预训练模型。

词表包括 所有合法的带音标的汉语拼音（如：chen1、yi1、fan1） 以及 非汉字单词（如：CEO、Paper、《、123）。
词表中汉语拼音可以事先给定，不能单独存在的声母、韵母不会出现在词表中。词表中非汉字部分由BPE算法得到。
词表中不存在中文汉字。

首先将输入的文本使用pypinyin包进行预处理，其中汉字被转换为对应汉语拼音，非汉字首先进行切分然后转化为词表中的子词。
```
>>> from pypinyin import Style, pinyin
# 如下图所示，此时非pinyin部分并未切分
>>> pinyin("对于这个APP，John的想法是首先有个idea，然后再与S-team（包括Jeff和Dean）讨论", style=Style.TONE3, errors=lambda x: str(x))
[['dui4'], ['yu2'], ['zhe4'], ['ge4'], ['APP，John'], ['de'], ['xiang3'], ['fa3'], ['shi4'], ['shou3'], ['xian1'], ['you3'], ['ge4'], ['idea，'], ['ran2'], ['hou4'],
 ['zai4'], ['yu3'], ['S-team（'], ['bao1'], ['kuo4'], ['Jeff'], ['he2'], ['Dean）'], ['tao3'], ['lun4']]
```
预训练模型以汉语拼音和非汉字单词构成的token作为输入，输出同样为汉语拼音和非汉字单词。然后会调用汉语输入法将之转换为汉语文本。

所以需要实现的部分有：
1. Tokenizer：主要是对非汉字文本的分词处理；
2. 模型训练：会参考中英文预训练模型的一些训练方法；
3. 拼音输入法：基于目前已有的研究或者工具。


# 时间进度表
2023/05/06 - 2023/05/20 毕业设计期间。优化拼音词表，寻找预训练策略；

2023/05/20 - 2023/06/20 完成预训练过程，基本要求是语言模型生成的拼音序列通顺、流畅；

2023/06/20 - 2023/06/27 完成拼音到汉字的转换并测试语言模型的实际效果；

# 项目进度
1. 提取悟道数据集中非汉字字符，构建词表
   - 使用Unicode编码值区分汉字与非汉字
   - 使用transformers库中pre-tokenization函数将非汉字字符串进行切分，切割符包括空格、标点符号。其中标点符号在切分结果中，空格不在
   - 对切分后的非汉字单词进行BPE算法构建非汉字词表。切分后的非汉字单词一共有2300w个，一共出现了98亿次，实验时发现全部使用运行速度太慢，考虑到前10w个单词的出现次数占比达到98.3293%，因此只选取出现次数最高的前10w个单词。
   - 将所有合法的拼音加入到BPE构成的词表中
目前问题，构成的词表中，许多子词是纯数字，根据《Do NLP Models Know Numbers? Probing Numeracy in Embeddings》,数字采用Character-level比sub word-level更加精确，下一步即使对应的调整。但是对于非纯数字的情况（50Hz）和数字后面是否加‘<\\w>’还要观察其他LM的情况。

# 项目思路讨论
1. 词表中拼音和非拼音部分为什么要分开？

首先汉语拼音是一个有限集合，分开首先可以节省BPE操作的次数；第二，汉语拼音中出现的子词，如ch、zh、ang、eng，这些字词在英文单词并没有在拼音中的特殊含义，如果这些子词在英文中被识别，猜测这样并不利于LM的训练；
同时，为了避免英文文本分词中出现“ran”这样可能被识别成汉语拼音的情况，我们在让汉语拼音都加上声调予以区分，如“ran1”。

2. 非拼音部分为什么不采用已有的tokenizer得到一个词表？

对于非拼音部分的分词，如果采用英文的tokenizer切分单词得到一个词表，考虑到英文文本中的单词，与汉语文本中会出现的英文单词，其分布有很大不同，比如中文文本中只有CEO、vivo、ipad、App这些固定的经常在中文文本中出现的单词，
而像an、the、we这些单词就出现的少，因此没有选用英文的tokenizer。而中文的tokenizer，尝试之后发现有很多词都识别成了[UNK]，OOV较为严重

3. 非汉语文本BPE算法执行的过程中选取前10w个单词是否合理？

观察使用全部单词和10w单词初始化的词表，主要的差距在于许多小众的unicode符号。观察Bert, GPT2等模型的词表，其中小众unicode字符较少
