# -*- coding: utf-8 -*-


import utils
from utils import FullwideMapping

_to_wide = FullwideMapping()
_to_wide.addFullwideMapping(ord(' '), u'\u3000')
_to_wide.addFullwideMapping(ord('\t'), None)
to_wide = _to_wide.to_wide


class SCParserException(Exception):
    pass


class SCParser:
    def __init__(self):
        self.reset()

    def reset(self):
        self.talking = False
        self.named = False
        self.voice_dir = ''

    def parse(self, script):
        result = [self.parse_line(lno+1, line) for lno, line in enumerate(script.splitlines())]
        results = '\n'.join(result)
        assert not self.talking and not self.named
        return results

    def parse_line(self, lno, line):
        if line.strip() == '':
            return ''
        if line.startswith('<'):
            return self.parse_lt(line)
        if line == 'EF5,on':    # bug? scsc_2020603
            # return ''
            line = 'EF 5,on'
        prefix = postfix = ''
        if line in ('VO vos_109_EA0902_0220', 'VO vos_209_EA0902_0220', 'VO vos_309_EA0902_0220'):
            # fix scsc_1090201 3090201
            self.talking = False
            prefix = '\\\n'
        func_name = line[:2]
        if ord('A') <= ord(func_name[0]) <= ord('Z'):
            if len(line) < 3 or line[2] == ' ':
                func = getattr(self, "parse_" + func_name)
                if func:
                    if self.talking:
                        print("[WARN] talking while executing: %s" % line)
                    return prefix + func(line[3:]) + postfix
            raise SCParserException("Unknown function in line: " + line)
        line = to_wide(line.rstrip())
        if line.startswith('「'):
            self.talking = True
            self.named = False
        elif self.talking:
            prefix = ''
        else:
            if self.named:
                raise SCParserException("Name after named(%d): %s" % (lno, line))
            self.named = True
            return 'name "%s"' % line
        if line.endswith('」'):
            # FIXME: in scsc_3080401: 90
            if line.count('「') <= line.count('」'):
                self.talking = False
                postfix = '\\'
        return '%s%s%s' % (prefix, line, postfix)

    def parse_lt(self, line):
        if line.endswith('>'):
            line = line[:-1]
            if line.startswith('<anm'):
                # TODO
                return ''
            if line.startswith('<se ') :
                return r'se "%s"' % (line[4:])
        raise NotImplementedError(line)

    # voice
    def parse_VO(self, param):
        params = param.split('_')
        _path = param
        # if len(params) >= 3 and params[1].isdigit():
            # _path = '%s/%s' % (params[1], param)
        return r'voice "%s\%s"' % (self.voice_dir, _path)

    # title
    def parse_TI(self, param):
        chapter, title = param.split(',')
        return 'title "%s", "%s"' % (to_wide(chapter), to_wide(title))

    # bgm
    def parse_MU(self, param):
        if param.strip() == '':
            return 'bgmstop'
        return r'bgm "bgm\%s.ogg"' % (param)

    # bg
    def parse_BG(self, param):
        if param == '':
            # FIXME
            param = 'map'
        elif param == 'color=255,255,255,255':
            param = 'black'
        else:
            if not param.isdigit():
                raise SCParserException(param)
            param = 'adv_bg%s' % (param)
        return 'bg_ "%s"' % (param)

    # chara
    def _gen_chara(self, param, pos):
        if param.endswith('」'):
            # 似乎是剧本自身的bug, 见 scsc_2010801: 150
            param = param[:-1]
        if param.startswith(',on'):
            if param[3:] == '':
                _time = 0
            elif param[3:].isdigit():
                _time = int(param[3:])
            else:
                raise NotImplementedError(param)
            return 'char_on %d, %d' % (pos, _time)
        if param == ',':
            # bug? 见 scsc_2010907: 50
            param = ''
        for c in param:
            if not c.isdigit() and c != '_':
                raise NotImplementedError(param)
        _r = param.split('_')
        if len(_r) <= 1:
            base = param
            param = ''
        elif param.endswith("_1_1"):
            base = param[:-4]
            param = ''
        elif param.endswith("_1_"):
            base = param[:-3]
            param = ''
        else:
            base = _r[0]
        assert not param.endswith('_')
        return 'char %d, "%s", "%s"' % (pos, base, param)
    def parse_C1(self, param):
        _r = param.split('_')
        return self._gen_chara(param, 1)
    def parse_C2(self, param):
        _r = param.split('_')
        return self._gen_chara(param, 2)
    def parse_C3(self, param):
        _r = param.split('_')
        return self._gen_chara(param, 3)
    def parse_C4(self, param):
        _r = param.split('_')
        return self._gen_chara(param, 4)
    def parse_C5(self, param):
        _r = param.split('_')
        return self._gen_chara(param, 5)
    def parse_C6(self, param):
        _r = param.split('_')
        return self._gen_chara(param, 6)
    def parse_C7(self, param):
        _r = param.split('_')
        return self._gen_chara(param, 7)
    # messagebox?
    def parse_FR(self, param):
        if param == '0' or param == '2':
            return 'texton_'
        if param == '':
            return 'textoff_'
        raise NotImplementedError(param)
    # unknown (input name?)
    def parse_NE(self, param):
        raise NotImplementedError(param)
    # effect
    def parse_EF(self, param):
        return 'trans ' + param[0]
        if param == '5,on': # fade out
            return '[trans time=2000][wt]'
        if param == '6,on': # fade in
            # fade out
            return '[trans time=2000][wt]'
        if param == '1,on': # unknown
            return '[trans time=2000][wt]'
        if param == '3,on': # unknown
            return '[trans time=2000][wt]'
        if param == '7,on': # unknown
            return '[trans time=2000][wt]'
        if param == '8,on': # unknown
            return '[trans time=2000][wt]'
        raise NotImplementedError(param)
    # wait?
    def parse_WA(self, param):
        assert param.isdigit() and param.strip() != ''
        time = int(param) * 1000 // 30
        return 'wa %s' % int(param)
