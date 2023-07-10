import ass
import math
import os


def transform_line(events: ass.Events):
    for index, line in enumerate(events.Line):
        if line.TYPE != ass.EventLineType.Dialogue:
            ass.log_warning('注释行，跳过')
            continue
        if line.Name == 'py_lable':
            ass.log_warning('处理行，跳过')
            continue
        # 读取特效标签，记录标签
        lable_list = list()
        for lable in line.Text.tag:
            # k轴标签
            if lable.effect_name in ['k', 'ko', 'kf']:
                lable_list.append(lable)
                # 复制一份
                events.repeat_line(index)
        # 没有k轴不处理
        if lable_list.__len__() == 0:
            ass.log_message(f"行{index}无需处理")
            continue
        # 重置层
        line.Layer = '1'
        # 注释参考行
        line.TYPE = ass.EventLineType.Comment
        # 删除原k轴，平移时间，添加fad，添加alpha
        for offset, lable in enumerate(lable_list, start=1):
            corrent_line = events.Line[index + offset]
            corrent_line.TYPE = ass.EventLineType.Dialogue
            corrent_line.Layer = str(offset + 1)
            corrent_line.Name = 'py_lable'
            # 删除原k轴
            rd = list()
            for lb in corrent_line.Text.tag:
                if lb.effect_name in ['k', 'ko', 'kf']:
                    rd.append(lb)
            for lb in rd:
                corrent_line.Text.tag.remove(lb)
            del rd
            # 平移
            if offset != 1:
                last_line = events.Line[index + offset - 1]
                # 上一行 减去 基准行 即为预偏移时间
                delta = last_line.Start.time - line.Start.time
                fp = round(int(lable_list[offset-2].effect_parameter)*0.01, 2)
                mill, second = math.modf(fp)
                mill = int(round(mill*1000))
                second = int(second)
                corrent_line.Start.time_offset(seconds=second, milliseconds=mill, last=delta)
            # 添加fad
            corrent_line.Text.insert_effect_tag('fad', 0, '(120,120)')
            # 添加alpha
            corrent_line.Text.insert_effect_tag('alpha', 0, 'ff')
            corrent_line.Text.insert_effect_tag('alpha', lable.effect_region, '0')
            if offset < lable_list.__len__():
                corrent_line.Text.insert_effect_tag('alpha', lable_list[offset].effect_region, 'ff')
        ass.log_message(f"行{index}处理完成")


if __name__ == '__main__':
    print("file name")
    path = input()
    f = open(path, encoding='utf-8-sig')
    doc = ass.ASSFile.parse_file(f)
    f.close()

    transform_line(doc.Events)

    os.rename(path, path+'.old')
    f = open(path, 'w+', encoding='utf-8-sig')
    doc.dump_to_file(f)
    f.close()
