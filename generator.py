#!/bin/python
# -*- coding: utf-8 -*-

import os

from mapngdecoder import decrypt

from scenario import MASceniaroManager
from scparser import SCParser
from visitor import Visitor


class MAGenerator:
    def __init__(self, root_dir, out_dir, encoding='gbk'):
        self.root_dir = root_dir
        self.out_dir = out_dir
        self.scenario_manager = MASceniaroManager(root_dir)
        self.parser = SCParser()
        self.encoding = encoding
        self.visitors = [
                RouteVisitor(self),
                TextVisitor(self),
                ]

    def generate(self):
        return [visitor.visit(self.scenario_manager) for visitor in self.visitors]

class TextVisitor(Visitor):
    def __init__(self, generator):
        self.generator = generator
        self.results = []

    def visit_talk(self, talk, section, chapter):
        talk_num = section.prefix * 100 + talk
        filename = os.path.join(self.generator.root_dir, 'download', 'scenario',
                "scsc_%d" % talk_num)
        with open(filename, 'rb') as f:
            # print("[DEBUG] Proceeding %s" % filename)
            script = decrypt(f.read()).decode('utf8')
            self.generator.parser.reset()
            self.generator.parser.voice_dir = chapter.id
            results = self.generator.parser.parse(script)
            self.results.append('*scene_%d' % talk_num)
            self.results.append('begin_scene %d' % talk_num)
            self.results.append(results)
            self.results.append('return')

    def end_visit(self, manager):
        outname = os.path.join(self.generator.out_dir, "10.txt")
        with open(outname, 'w', encoding=self.generator.encoding) as f:
            f.write('\n'.join(self.results))

class RouteVisitor(Visitor):
    def __init__(self, generator):
        self.generator = generator
        self.results = {}

    def begin_visit(self, manager):
        self.results = {}

    def begin_chapter(self, chapter):
        c = "chapter_%d" % chapter.id
        self.results[c] = ["*"+c]

    def end_chapter(self, chapter):
        c = "chapter_%d" % chapter.id
        self.results[c].append("return")

    def begin_section(self, section, chapter):
        c = "chapter_%d" % chapter.id
        s = "section_%d" % section.prefix
        self.results[c].append("gosub *"+s)
        self.results[s] = ["*"+s]

    def end_section(self, section, chapter):
        s = "section_%d" % section.prefix
        self.results[s].append("return")

    def visit_talk(self, talk, section, chapter):
        s = "section_%d" % section.prefix
        talk_num = section.prefix * 100 + talk
        self.results[s].append("gosub *scene_%d" % talk_num)

    def end_visit(self, manager):
        outname = os.path.join(self.generator.out_dir, '08.txt')
        with open(outname, 'w', encoding=self.generator.encoding) as f:
            f.write('\n\n'.join('\n'.join(l) for l in self.results.values()))


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('''Usage:
    python3 {program_name} <save_dir> <out_dir>
'''.format(program_name=sys.argv[0]))
        sys.exit(0)

    OUT_DIR = sys.argv[2]
    os.makedirs(OUT_DIR, exist_ok=True)

    generator = MAGenerator(sys.argv[1], OUT_DIR)
    generator.generate()
