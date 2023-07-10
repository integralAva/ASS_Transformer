from ass.events import Events


class ASSFile(object):
    def __init__(self, data_dict: dict = None):
        if data_dict is not None:
            self.data_dict = data_dict
            if 'Events' in data_dict:
                self.Events = Events.parse(data_dict['Events'])

    @classmethod
    def parse_file(cls, f):
        section_name = ''
        section_dict = dict()

        for i, line in enumerate(f):
            if i == 0:
                bom_seqeunces = ("\xef\xbb\xbf", "\xff\xfe", "\ufeff")
                if any(line.startswith(seq) for seq in bom_seqeunces):
                    raise ValueError("编码格式有误")

            # 循环包含换行，在这里去除换行
            line = line.strip()
            # 跳过注释行
            if not line or line.startswith(';'):
                continue

            # 内容标记
            if line.startswith('[') and line.endswith(']'):
                section_name = line[1:-1]
                section_dict[section_name] = str()
                continue

            # 跳过空行
            if ':' not in line:
                continue

            # 还原内容
            if section_name.__len__() != 0:
                section_dict[section_name] += line + '\n'

        return cls(section_dict)

    def self_update(self):
        if 'Events' in self.data_dict:
            self.data_dict['Events'] = ''
            for line in self.Events.Line:
                self.data_dict['Events'] += line.to_ass() + '\n'

    def dump_to_file(self, f):
        # dump的基础是有序字典
        encoding = getattr(f, 'encoding')
        if encoding != 'utf-8-sig':
            raise ValueError("NOT correct encoding")

        self.self_update()
        for section, data in self.data_dict.items():
            f.write(f'[{section}]\n')
            f.write(data)
            f.write('\n')
