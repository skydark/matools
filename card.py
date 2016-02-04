#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from os import path
from urllib.request import urlopen
from urllib.error import HTTPError
from multiprocessing.dummy import Pool as ThreadPool
import json
import sqlite3

from reader import Reader
from mapngdecoder import decrypt


class MACardList:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.cards = []
        self.load()

    def load(self):
        _path = path.join(self.root_dir, 'database', 'master_card')
        with open(_path, 'rb') as _f:
            buf = Reader(_f)
            count = buf.read_int()  # 卡牌数量
            offsets = [0] * count
            self.cards = cards = [None] * count
            for i in range(count):
                cards[i] = MACard()
                offsets[i] = buf.read_int()
            for i, card in enumerate(cards):
                buf.seek(offsets[i])
                card.load(buf)

class MACard:
    FIELDS = '''
        master_card_id country_id name/s char_description/s
        skill_kana/s skill_name/s skill_description/s
        illustrator/s cost rarity extra eye_y sale_price
        compound_target_id compound_result_id
        base_hp base_power max_lv image1_id image2_id character_id
        _always_0 data_type grow_type
        grow_name/s growth_rate_text/s skill_type form_id distinction
        card_version attack_type lvmax_hp lvmax_power base_holo_hp base_holo_power
        lvmax_holo_hp lvmax_holo_power max_lv_holo compound_type
    '''.split()
    # grow_type: 1-平均 2-早熟 3-晚成
    # distinction: 1-男 2-女
    # attack_type: 力量属性

    BASE_URL = 'http://MA.webpatch.sdg-china.com/MA/PROD/2/'
    URLS = {
        "full_thumbnail_chara_{.image1_id}.png":
            BASE_URL + 'card_full/full_thumbnail_chara_{.image1_id}?cyt=1',
        "full_thumbnail_chara_{.image2_id}.png":
            BASE_URL + 'card_full_max/full_thumbnail_chara_{.image2_id}?cyt=1',
        "full_thumbnail_chara_{.image1_id}_horo.png":
            BASE_URL + 'card_full_h/full_thumbnail_chara_{.image1_id}_horo?cyt=1',
        "full_thumbnail_chara_{.image2_id}_horo.png":
            BASE_URL + 'card_full_h_max/full_thumbnail_chara_{.image2_id}_horo?cyt=1',
    }

    def __init__(self):
        pass

    def load(self, buf):
        I = buf.read_int
        S = buf.read_str
        for field in self.FIELDS:
            if field.endswith('/s'):
                setattr(self, field[:-2], S())
            else:
                setattr(self, field, I())

    def download_full_card(self, downloader):
        for name, url in self.URLS.items():
            downloader.download(name.format(self), url.format(self))

class MACardToDB:
    def __init__(self, cards):
        self.cards = cards
        self.db = None
        self.table_name = 'cards'
        self.fields = [(
            field[:-2] if field.endswith('/s') else field,
            'text' if field.endswith('/s') else 'integer'
            ) for field in MACard.FIELDS]
        self.add_query = "insert into %s (%s) values (%s)" % (
                self.table_name,
                ', '.join(field for field, type in self.fields),
                ', '.join(['?'] * len(self.fields))
                )

    def dump(self, db_name):
        self.db = self.create_db(db_name)
        for card in self.cards:
            self.add_card(card, commit=False)
        self.db.commit()

    def dump_json(self, json_name=None):
        ret = [card.__dict__ for card in self.cards]
        if json_name is None:
            return json.dumps(ret)
        with open(json_name, 'w') as f:
            json.dump(ret, f)

    def create_db(self, db_name):
        db = sqlite3.connect(db_name)
        sql = "create table if not exists %s (%s)" % (
                self.table_name,
                ', '.join('%s %s' % (f, t) for f, t in self.fields))
        db.execute(sql)
        db.commit()
        return db

    def add_card(self, card, commit=True):
        values = [getattr(card, field) for field, type in self.fields]
        self.db.execute(self.add_query, values)
        if commit:
            self.db.commit()


class MADownloader:
    def __init__(self, output_dir, post=decrypt, dumper=None):
        self.output_dir = output_dir
        self.post = post
        if dumper is not None:
            self.dumper = dumper

    def download(self, name, url):
        _path = path.join(self.output_dir, name)
        if path.exists(_path):
            # cached
            return
        print('[DEBUG] Downloading ' + name)
        try:
            src = urlopen(url).read()
            data = self.post(src)
        except Exception as e:
            print(e)
            return
        return self.dumper(_path, data)

    def dumper(self, _path, data):
        with open(_path, 'wb') as f:
            f.write(data)

class MultiDownloader:
    def __init__(self, output_dir, post=decrypt, dumper=None, threads=6):
        self.output_dir = output_dir
        self.post = post
        if dumper is not None:
            self.dumper = dumper
        self.url_map = []
        self.threads = threads

    def download(self, name, url):
        _path = path.join(self.output_dir, name)
        if path.exists(_path):
            # cached
            return
        self.url_map.append((_path, url))

    def _download(self, pair):
        _path, url = pair
        # print('[DEBUG] Downloading ' + _path)
        try:
            src = urlopen(url).read()
            data = self.post(src)
        except Exception as e:
            if isinstance(e, HTTPError) and e.getcode() == 404:
                return
            print('[ERROR] error occured while downloading ' + _path)
            print('        ' + url)
            print('        ' + str(e))
            return
        print('[DEBUG] %s is downloaded' % _path)
        return self.dumper(_path, data)

    def dumper(self, _path, data):
        with open(_path, 'wb') as f:
            f.write(data)

    def run(self):
        print("Start downloading %d files..." % len(self.url_map))
        pool = ThreadPool(self.threads)
        results = pool.map(self._download, self.url_map)
        pool.close()
        pool.join()


if __name__ == '__main__':
    cardlist = MACardList('save')
    MACardToDB(cardlist.cards).dump('ma.db')
    MACardToDB(cardlist.cards).dump_json('ma.json')
    sys.exit(0)

    if len(sys.argv) < 3:
        print('''Usage:
    python3 {program_name} <save_dir> <out_dir>
'''.format(program_name=sys.argv[0]))
        sys.exit(0)

    OUT_DIR = sys.argv[2]
    os.makedirs(OUT_DIR, exist_ok=True)

    cardlist = MACardList(sys.argv[1])
    # downloader = MADownloader(OUT_DIR)
    downloader = MultiDownloader(OUT_DIR, threads=8)
    for card in cardlist.cards:
        card.download_full_card(downloader)
    downloader.run()
