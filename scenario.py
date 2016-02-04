#!/bin/python
# -*- coding: utf-8 -*-

import os

from reader import Reader

class Chapter:
    id = 0
    i = 0
    title = ''
    sections = None


class Section:
    prefix = 0
    title = ''
    battle_num = 0
    talks = None


class MASceniaroManager:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.scenario = {}
        self.load()

    def get_scenario(self, country):
        return self.scenario[country]

    def load(self):
        _path = os.path.join(self.root_dir, 'database', 'master_scol')
        with open(_path, 'rb') as _f:
            buf = Reader(_f)
            I, S = buf.read_int, buf.read_str
            def assert_int(i):
                if I() != i:
                    buf.error("Not valid scenario data")
            count = I()     # 剧情章节总计
            for chapter in range(count):
                chapter_id = I()
                chapter = self.scenario[chapter_id] = Chapter()
                assert_int(0)
                chapter.id = chapter_id
                chapter.i = I()
                chapter.title = S()
                chapter.sections = []
                for i in range(I()):
                    section = Section()
                    section.prefix = I()
                    section.title = S()
                    section.battle_num = I()
                    section.talks = []
                    for j in range(I()):
                        section.talks.append(I())
                    chapter.sections.append(section)
                if chapter_id < 400:
                    assert_int(0xc8)
                else:
                    assert_int(0xa1)
            buf.end()

    def visit(self, visitor):
        for chapter in self.scenario.values():
            visitor.begin_chapter(chapter)
            self.visit_chapter(visitor, chapter)
            visitor.end_chapter(chapter)

    def visit_chapter(self, visitor, chapter):
        for section in chapter.sections:
            visitor.begin_section(section, chapter)
            self.visit_section(visitor, section, chapter)
            visitor.end_section(section, chapter)

    def visit_section(self, visitor, section, chapter):
        for talk in section.talks:
            visitor.visit_talk(talk, section, chapter)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('''Usage:
    python3 {program_name} <save_dir> <out_dir>
'''.format(program_name=sys.argv[0]))
        sys.exit(0)

    scenario = MASceniaroManager(sys.argv[1])
    scenario.load()

