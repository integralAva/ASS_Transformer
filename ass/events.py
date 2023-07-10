import re
from ass.time import ASSTime
from ass.logging import *
import copy

__all__ = [
    'EffectTag',
    'EventLineType',
    'EventLine',
    'Events',
    'DialogueText'
]

_effect_re_list: list[str] = [
    r'i+[0-1]',
    r'b+[0-1]',
    r'u+[0-1]',
    r's+[0-1]',
    r'bord+.*[0-9]',
    r'xbord+.*[0-9]',
    r'ybord+.*[0-9]',
    r'shad+.*[0-9]',
    r'xshad+.*[0-9]',
    r'yshad+.*[0-9]',
    r'be+[0-1]',
    r'blur+.*[0-9]'
    r'fn+.*\w',
    r'fs+.*[0-9]',
    r'fscy+.*[0-9]',
    r'fscx+.*[0-9]',
    r'fsp+.*[0-9]',
    r'fr+.*[0-9]',
    r'frx+.*[0-9]',
    r'fry+.*[0-9]',
    r'frz+.*[0-9]',
    r'fax+.*[0-9]',
    r'fay+.*[0-9]',
    r'^[0-9][ac]&.*?&',
    r'[a][n]*[0-9]',
    r'[Kk]+[of]*.*[0-9]',
    r'r+.*\w',
    r'pos\(.*?\)',
    r'move\(.*?\)',
    r'org\(.*?\)',
    r'fad\(.*?\)',
    r't\(.*?\)',
    r'clip\(.*?\)',
    r'iclip\(.*?\)'
]

_effect_re_dict: dict[str:tuple[str, str]] = {
    r'i+[0-1]': (r'i', r'[0-1]'),
    r'b+[0-1]': (r'i', r'[0-1]'),
    r'u+[0-1]': (r'i', r'[0-1]'),
    r's+[0-1]': (r'i', r'[0-1]'),
    r'bord+[0-9]+': (r'bord', r'[0-9]+'),
    r'xbord+[0-9]+': (r'xbord', r'[0-9]+'),
    r'ybord+[0-9]+': (r'ybord', r'[0-9]+'),
    r'shad+[0-9]+': (r'shad', r'[0-9]+'),
    r'xshad+[0-9]+': (r'xshad', r'[0-9]+'),
    r'yshad+[0-9]+': (r'yshad', r'[0-9]+'),
    r'be+[0-1]': (r'be', r'[0-1]'),
    r'blur+[0-9]+': (r'blur', r'[0-9]+'),
    r'fn+.*\w': (r'fn', r'[^fn].*'),
    r'fs+[0-9]+': (r'fs', r'[0-9]+'),
    r'fscy+[0-9]+': (r'fscy', r'[0-9]+'),
    r'fscx+[0-9]+': (r'fscx', r'[0-9]+'),
    r'fsp+[0-9]+': (r'fsp', r'[0-9]+'),
    r'fr+[0-9]+': (r'fr', r'[0-9]+'),
    r'frx+[0-9]+': (r'frx', r'[0-9]+'),
    r'fry+[0-9]+': (r'fry', r'[0-9]+'),
    r'frz+[0-9]+': (r'frz', r'[0-9]+'),
    r'fax+[0-9]+': (r'fax', r'[0-9]+'),
    r'fay+[0-9]+': (r'fay', r'[0-9]+'),
    r'^[0-9][ac]&.*?&': (r'^[0-9][ac]', r'&.*?&'),
    r'[a][n]*[0-9]': (r'[a][n]*', r'[0-9]'),
    r'[Kk]+[of]*.*[0-9]': (r'[Kk]+[of]*', r'[0-9]+'),
    r'r+.*\w': (r'r', r'[^r].*'),
    r'pos\(.*?\)': (r'pos', r'\(.*?\)'),
    r'move\(.*?\)': (r'move', r'\(.*?\)'),
    r'org\(.*?\)': (r'org', r'\(.*?\)'),
    r'fad\(.*?\)': (r'fad', r'\(.*?\)'),
    r't\(.*?\)': (r't', r'\(.*?\)'),
    r'clip\(.*?\)': (r'clip', r'\(.*?\)'),
    r'iclip\(.*?\)': (r'iclip', r'\(.*?\)')
}


class EffectTag(object):
    """特效标签类"""
    def __init__(self, name: str = '', region: int = 0, parameter: str = ''):
        """
        生成特效标签
        :param name: 特效标签名称
        :param parameter: 参数，必要时需括号
        :param region: 作用域，即插入字符串的位置
        :return: None
        """
        self.effect_name = name
        self.effect_parameter = parameter
        self.effect_region = region

    @property
    def text(self):
        """返回合成文本"""
        return '\\' + self.effect_name + self.effect_parameter


class DialogueText(object):
    def __init__(self, text: str = '', tag: list[EffectTag] = None):
        """
        :param text: 源文本，不包含特效标签
        :param tag: 特效标签列表
        """
        if tag is None:
            tag = []
        self.text = text
        self.tag = tag

    @classmethod
    def prase_from_ass(cls, raw_text: str):
        my_text = str()
        my_lable_list = list()
        pointer = 0
        # 还原文本
        for t in re.split(r'\{.*?}', raw_text):
            my_text += t
        # 匹配特效标签
        lable_iter = re.finditer(r'\{.*?}', raw_text)
        # 分析特效标签
        for lable in lable_iter:
            # 掐头去尾分割 {\a\b} -> a,b
            lable_text = lable.group()[2:-1].split('\\')
            # 算region
            region = lable.start() - pointer
            pointer += len(lable.group())
            for item in lable_text:
                if item == '':
                    continue
                my_lable_list.append(EffectTag(item, region))
        # 解析特效标签名称与参数
        expression = None
        for lable in my_lable_list:
            # 逐个尝试匹配
            for re_expression in _effect_re_list:
                ans = re.match(re_expression, lable.effect_name)
                if ans is not None:
                    expression = re_expression
                    break
            if expression is not None:
                name, para = re.match(_effect_re_dict[expression][0], lable.effect_name),\
                             re.search(_effect_re_dict[expression][1], lable.effect_name)
                if name is not None and para is not None:
                    lable.effect_name, lable.effect_parameter = name.group(), para.group()
                expression = None
        return cls(my_text, my_lable_list)

    def to_ass(self):
        """合成特效标签输出文本"""
        # 无特效标签直接输出
        if self.tag.__len__() == 0:
            return self.text
        # 记录每个位置的标签
        tag_dict = dict()
        tag_region_list = list()
        # 合并在同样作用域的标签
        for tag in self.tag:
            if tag.effect_region in tag_dict:
                tag_dict[tag.effect_region] += tag.text
            else:
                # 这个作用域没有标签，新建一个
                tag_dict[tag.effect_region] = tag.text
                tag_region_list.append(tag.effect_region)
        # 合成
        # 反向方便索引
        tag_region_list.sort(reverse=True)
        pointer = -1
        content = str()
        # index 作用域索引
        for index in tag_region_list:
            # 超出范围归位尾行，提高耐造性
            if index >= self.text.__len__():
                # 直接加到结尾
                content += '{' + tag_dict.get(index) + '}'
                continue
            # 索引在最后一位
            if pointer == -1:
                content = '{' + tag_dict.get(index) + '}' + self.text[index:] + content
                pointer = index
                continue
            content = '{' + tag_dict.get(index) + '}' + self.text[index:pointer] + content
            pointer = index
        return content

    def insert_effect_tag(self, name: str, region: int, parameter: str):
        """
        插入特效标签
        :param name: 标签名称
        :param parameter: 参数
        :param region: 插入位置
        :return: None
        """
        self.tag.append(EffectTag(name, region, parameter))


class EventLineType:
    Dialogue = 'Dialogue'
    Comment = 'Comment'


class EventLine(object):
    # 该行的前标签 如 Dialogue
    TYPE = EventLineType.Comment
    # 该行的格式
    Format = ['Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']
    # 预设的属性
    Layer = '0'
    Style = ''
    Name = ''

    def __init__(self, kwargs: dict = None):
        # 自定义属性
        if kwargs is not None:
            for name, val in kwargs.items():
                setattr(self, name, val)
        # 文本管理
        if not hasattr(self, 'Text'):
            self.Text = ''
        self.Text = DialogueText.prase_from_ass(self.Text)
        # 时间管理
        if not hasattr(self, 'Start'):
            self.Start = None
        self.Start = ASSTime(self.Start)
        if not hasattr(self, 'End'):
            self.End = None
        self.End = ASSTime(self.End)

    @classmethod
    def parse(cls, line: str, parameter_format: list | str = None, type_name: str = None):
        """
        解析行
        :param line: （去除了行类型的）源行
        :param type_name: 行类型
        :param parameter_format: 格式
        :return: EventLine实例
        """
        if parameter_format is None:
            parameter_format = cls.Format
        if isinstance(parameter_format, str):
            # 适配没有被分割成列表的纯文本
            parameter_format = parameter_format.replace(' ', '').split(',')
        # 适配不提供类型的情况，尝试获取类型
        if type_name is None:
            type_name, _, content = line.partition(':')
            line = content.lstrip()
            if content.__len__() == 0:
                raise ValueError("格式有误")
        # 分割数据
        parts = line.split(',')
        if parts.__len__() != parameter_format.__len__():
            raise ValueError("格式有误")
        doc = cls(dict(zip(parameter_format, parts)))
        doc.Format = parameter_format
        doc.TYPE = type_name
        return doc

    def total_seconds(self):
        return self.End.time - self.Start.time

    def format_attr(self):
        data = list()
        for name in self.Format:
            obj = getattr(self, name, '0')
            if isinstance(obj, str):
                data.append(obj)
            else:
                data.append(obj.to_ass())
        return ','.join(data)

    def to_ass(self):
        return self.TYPE + ': ' + self.format_attr()


class Events(object):
    Format = ['Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']

    def __init__(self, line_list: list[EventLine] = None, kwargs: dict = None):
        self.Line = list()
        if line_list is not None:
            self.Line = line_list
        if kwargs is not None:
            for name, val in kwargs.items():
                setattr(self, name, val)

    @classmethod
    def parse(cls, data: str | list):
        """
        解析Event内容
        :param data: 传入源数据，可以是每一行的文本组成的列表形式
        :return: Events实例
        """
        doc = cls()
        if isinstance(data, str):
            data = data.split('\n')
        for line in data:
            type_name, _, content = line.partition(':')
            content = content.lstrip()
            if content.__len__() == 0:
                log_warning(f"Line read fail with {line}")
                continue
            if type_name == 'Format':
                content = content.replace(' ', '')
                doc.Format = content.split(',')
                log_message(f"Format {content}")
                continue
            log_message(f"{type_name} Detected")
            doc.Line.append(EventLine.parse(content, doc.Format, type_name))
        return doc

    def insert_line(self, line: EventLine, index: int = None, is_forward: bool = False):
        """
        插入行
        :param line: EventLine实例
        :param index: 位置，起始为0
        :param is_forward: 向前插入
        :return: None
        """
        if index is None:
            index = self.Line.__len__()
        if not is_forward:
            index += 1
        self.Line.insert(index, copy.deepcopy(line))

    def delete_line(self, index: int = None):
        """
        删除行
        :param index: 位置，起始为0
        :return: None
        """
        if index is None:
            index = self.Line.__len__() - 1
        self.Line.pop(index)

    def repeat_line(self, index: int = None):
        """
        重复行
        :param index: 位置，起始为0
        :return: None
        """
        if index is None:
            index = self.Line.__len__()
        self.Line.insert(index+1, copy.deepcopy(self.Line[index]))
