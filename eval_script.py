#!/usr/bin/env python
# coding=utf-8
"""
作者：林金城
邮箱：jinchengll@qq.com
描述：本脚本用来评估视频描述等任务的结果质量，评价指标有：
        - CIDEr
        - Bleu_4
        - Bleu_3
        - Bleu_2
        - Bleu_1
        - ROUGE_L
        - METEOR
"""
import hashlib
import io
import json
import os
import pylab
import sys

sys.path.append('./coco-caption/')
from pycocotools.coco import COCO
from pycocoevalcap.eval import COCOEvalCap


#############################组件定义#############################
class CocoAnnotations:
    def __init__(self):
        self.images = []
        self.annotations = []
        self.img_dict = {}
        info = {
            "year": 2016,
            "version": '1',
            "description": 'CaptionEval',
            "contributor": 'Jincheng Lin',
            "url": 'https://github.com/jinchengll/',
            "date_created": '',
        }
        licenses = [{
            "id": 1,
            "name": "test",
            "url": "test",
        }]
        self.res = {"info": info,
                    "type": 'captions',
                    "images": self.images,
                    "annotations": self.annotations,
                    "licenses": licenses,
                    }

    def get_image_dict(self, img_name):
        image_hash = int(int(hashlib.sha256(img_name).hexdigest(), 16) % sys.maxint)
        if image_hash in self.img_dict:
        	# 出现相同的hash值，判断其是否是同一个文件名，不同就发生碰撞，结束。
        	assert self.img_dict[image_hash] == img_name, 'hash colision: {0}: {1}'.format(image_hash, img_name)
        else:
            self.img_dict[image_hash] = img_name
        image_dict = {"id": image_hash,
                      "width": 0,
                      "height": 0,
                      "file_name": img_name,
                      "license": '',
                      "url": img_name,
                      "date_captured": '',
                      }
        return image_dict, image_hash

    def generator_json(self, txt_file, json_file):
        count = 0
        with open(txt_file, 'r') as opfd:
            for line in opfd:
                count += 1
                id_sent = line.strip().split('\t')
                assert len(id_sent) == 2
                sent = id_sent[1].decode('ascii', 'ignore')
                image_dict, image_hash = self.get_image_dict(id_sent[0])
                self.images.append(image_dict)
                self.annotations.append({
                    "id": len(self.annotations) + 1,
                    "image_id": image_hash,
                    "caption": sent,
                })
                if count % 1000 == 0:
                    print 'Processed %d ...' % count
        with io.open(json_file, 'w', encoding='utf-8') as fd:
            fd.write(unicode(json.dumps(self.res, ensure_ascii=True, sort_keys=True, indent=2, separators=(',', ': '))))


class CocoResFormat:
    def __init__(self):
        self.res = []
        self.caption_dict = {}

    def generator_json(self, txt_file, json_file):
        count = 0
        with open(txt_file, 'r') as opfd:
            for line in opfd:
                count += 1
                id_sent = line.strip().split('\t')[-2:]
                assert len(id_sent) == 2
                sent = id_sent[1].decode('ascii', 'ignore')
                img_id = int(int(hashlib.sha256(id_sent[0]).hexdigest(), 16) % sys.maxint)
                imgid_sent = {}
                if img_id in self.caption_dict:
                    assert self.caption_dict[img_id] == sent
                else:
                    self.caption_dict[img_id] = sent
                    imgid_sent['image_id'] = img_id
                    imgid_sent['caption'] = sent
                    self.res.append(imgid_sent)
                if count % 100 == 0:
                    print 'Processed %d ...' % count
        with io.open(json_file, 'w', encoding='utf-8') as fd:
            fd.write(
                unicode(json.dumps(self.res, ensure_ascii=False, sort_keys=True, indent=2, separators=(',', ': '))))


##################################计算部分######################################
caption_output_path = 'data/caption_output'
result_file = 'result.txt'
references_txt_file = 'data/lable_references/references.txt'
references_json_file = 'data/lable_references/references.json'

def main():
    # pylab.rcParams['figure.figsize'] = (10.0, 8.0)
    # json.encoder.FLOAT_REPR = lambda o: format(o, '.3f')

    # 获得output文件列表
    captions_file_names = os.listdir(caption_output_path)
    captions_file_names.sort(key=lambda x: int(x.split('_')[0]))
    # 如果不存在的话，先生成references.json文件
    if not os.path.exists(references_json_file):
        cas = CocoAnnotations()
        cas.generator_json(references_txt_file, references_json_file)
        print 'Created json references in %s' % references_json_file

    f_result = open(result_file, 'w')
    # 记录最大值
    max_score = {}
    # 加载reference.json文件到评估模型
    coco = COCO(references_json_file)
    # 遍历计算每个描述文件的结果
    for file_name in captions_file_names:
        epoch, name = file_name[:file_name.index('_')], file_name[file_name.index('_')+1:]
        print '\n\n.....' + epoch + ' is calculate.............'
        # 生成pre_sents的json文件
        prediction_txt_file = os.path.join(caption_output_path, file_name)
        predictions_json_file = 'data' + '/{0}.json'.format(file_name[:file_name.index('.')])
        crf = CocoResFormat()
        crf.generator_json(prediction_txt_file, predictions_json_file)
        # 计算得分
        coco_res = coco.loadRes(predictions_json_file)
        coco_eval = COCOEvalCap(coco, coco_res)
        coco_eval.evaluate()
        # 输出和保存结果
        f_result.write('\n' + '-' * 10 + epoch + ' epcho' + '-' * 10 + '\n')
        for metric, score in coco_eval.eval.items():
            print '%s: %.3f' % (metric, score)
            f_result.write('%s: %.3f\n' % (metric, score))
            # 记录最大值
            if not metric in max_score or max_score[metric] < score:
                max_score[metric] = score
        # 删除生成的prediction的json文件
        os.remove(predictions_json_file)

        print '............compled.....................'
    # 输出并保存最大值
    print '\n............MAXMAX.....................'
    f_result.write('-' * 10 + 'MAXMAX' + '-' * 10 + '\n')
    for key, value in max_score.items():
        print '%s: %.3f' % (key, value)
        f_result.write('%s: %.3f\n' % (key, value))
    f_result.close()


if __name__ == "__main__":
    main()
