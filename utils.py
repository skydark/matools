# -*- coding: utf-8 -*-

import os

def cancel_if_exist(f):
    def _wrapped(_path, *arg, **kwarg):
        if not os.path.exists(_path):
            return f(_path, *arg, **kwarg)
    return _wrapped


class FullwideMapping:
    def __init__(self):
        _fullwide_map = [ chr(65248+i) for i in range(128)]
        self._fullwide_map = dict(enumerate(_fullwide_map))

    def addFullwideMapping(self, _from, _to):
        self._fullwide_map[_from] = _to

    def to_wide(self, s):
        return s.translate(self._fullwide_map)


_id = lambda x: x

def copyfile(src, dst, overwrite=False, decrypt=_id):
    if os.path.isfile(dst) and not overwrite:
        return
    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            fdst.write(decrypt(fsrc.read()))


def copytree(src, dst, overwrite=False, decrypt=_id):
    names = os.listdir(src)
    os.makedirs(dst, exist_ok=True)
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if os.path.isdir(srcname):
            copytree(srcname, dstname, overwrite=overwrite, decrypt=decrypt)
        else:
            copyfile(srcname, dstname, overwrite=overwrite, decrypt=decrypt)

def copyfiles(src, dst, filter=lambda n: True, overwrite=False, decrypt=_id,
        tranformer=_id):
    names = os.listdir(src)
    os.makedirs(dst, exist_ok=True)
    for name in names:
        if filter(name):
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, tranformer(name))
            copyfile(srcname, dstname, overwrite=overwrite, decrypt=decrypt)
