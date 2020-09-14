## 视频描述任务评估模型 ##
## Video Captioning Evaluation ##

### 主要内容
作者：jinchengll

基于[COCO Caption Evaluation page](https://github.com/tylin/coco-caption)实现使用自动指标对Video captioning任务的结果进行评估。

**它提供以下类型的得分：**
1. CIDEr
2. Bleu_4
3. Bleu_3
4. Bleu_2
5. Bleu_1
6. ROUGE_L
7. METEOR

### 环境配置
#### java
1. jdk8
#### python
更换清华源，更换方式自行查找。
1. python = 2.7
2. numpy=1.10.1
3. matplotlib=1.5.1
4. scikit-image=0.12.3

### 如何使用

1. **获取这份代码** `git clone https://github.com/jinchengll/caption-eval.git`
2. **进入到目录** `cd caption-eval`
2. **获取coco evaluation 脚本** `sh get_coco_scripts.sh`
3. 将你的正确的描述格式化成与`data/lable_references/references.txt`一致
4. 将你的模型输出文字格式化成与`data/caption_output/20_predicted_sentences.txt`一致，在`caption_output`文件夹下可以放置多个输出文件，例如：`20_predicted_sentences.txt`代表模型第20次训练得到的结果。因此如果有多个输出可以模仿这个样式。然而如果你只需要评估一个输出，你也需要以类似的方式命名你的文件：`XXX_predicted_sentences.tx`
5. 在caption-eval文件下执行`eval_script.py`代码：`python eval_script.py`
6. 最终结果保存在：`caption-eval/result.txt`

### 联系
有任何问题可以联系`jinchengll@qq.com`
