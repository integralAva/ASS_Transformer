import os
import ass
import re


def transform(src: ass.Document) -> ass.Document:
    # 重置层
    for line in src.events:
        line.layer = 1
    # 重置特效标签
    line_index = 0
    for line in src.events:
        text = line.text
        # 匹配特效标签
        lable_list = re.findall(r'\{.*?}', text)
        if len(lable_list) != 0:
            # 删除非必要特效标签
            index = 0
            for lable in lable_list:
                lable: str
                # 掐头去尾
                lable = lable[2:-1]
                # 切割
                delete_lable = list()
                lable_set = lable.split('\\')
                for item in lable_set:
                    if item == '':
                        delete_lable.append(item)
                        continue
                    if item[0] != 'k':
                        # 不是k轴？真不熟，进行一个切割
                        delete_lable.append(item)
                for item in delete_lable:
                    lable_set.remove(item)
                # 重新添加首尾
                lable_list[index] = '{\\' + '\\'.join(n for n in lable_set) + '}'
                index += 1
            # 重新组合写入
            new_text = ''
            raw_list = re.split(r'\{.*?}', text)
            new_text += raw_list[0]
            for count in range(1, len(raw_list)):
                new_text += lable_list[count-1] + raw_list[count]
            # 去除空特效标签
            new_text = new_text.replace('{\\}', '')
            # 写入
            src.events[line_index].text = new_text
        line_index += 1
    return src


if __name__ == '__main__':
    print("file name")
    path = './loVe-r.ass'
    f = open(path, encoding='utf-8-sig')
    doc = ass.parse(f)
    f.close()
    os.rename(path, path+'.old')

    doc = transform(doc)
    f = open(path, 'w+', encoding='utf-8-sig')
    doc.dump_file(f)
    f.close()
