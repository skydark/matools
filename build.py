#/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from card import MACardList, MACardToDB
from generator import MAGenerator
from utils import copytree, copyfiles
from mapngdecoder import decrypt


def build_viewer_face(root_dir, out_dir):
    copyfiles(os.path.join(root_dir, 'download', 'image', 'face'), out_dir,
            decrypt=decrypt, tranformer=lambda n: n+'.png')

def build_viewer_card(root_dir, out_dir):
    copyfiles(os.path.join(root_dir, 'download', 'image', 'card'), out_dir,
            decrypt=decrypt, tranformer=lambda n: n+'.png')


def build_viewer_data(root_dir, path, var_name):
    cardlist = MACardList(root_dir)
    dumper = MACardToDB(cardlist.cards)
    # dumper.dump('ma.db')
    json = dumper.dump_json()
    with open(path, 'w') as f:
        f.write('%s=%s;' % (var_name, json))


def build_ons_script(root_dir, out_dir):
    MAGenerator(root_dir, out_dir).generate()


def build_que_adv(decrypted, path):
    from io import BytesIO
    try:
        from PIL import Image
    except ImportError as e:
        print("PIL未安装，无法处理对话框图像，忽略")
        return
    im = Image.open(BytesIO(decrypted)).convert('RGBA')
    im = im.crop((0, 0, 960, 250))
    im.save(path)


def build_ons_data(root_dir, out_dir):
    build_ons_script(root_dir, out_dir)
    se_dir = os.path.join(root_dir, 'download', 'sound')
    print("复制bgm中...")
    copyfiles(se_dir, os.path.join(out_dir, "bgm"), lambda n: n.startswith('bgm'))
    print("复制音效中...")
    copyfiles(se_dir, os.path.join(out_dir, "se"), lambda n: n.startswith('se'))
    adv_dir = os.path.join(root_dir, 'download', 'image', 'adv')
    print("解密背景图片中...")
    copyfiles(adv_dir, os.path.join(out_dir, 'bgimage'),
            lambda n: n.startswith('adv_bg'),
            decrypt=decrypt, tranformer=lambda n: n+'.png')
    copyfiles(os.path.join(root_dir, 'download', 'rest'),
            os.path.join(out_dir, 'bgimage'),
            lambda n: n == 'exp_map_bg',
            decrypt=decrypt, tranformer=lambda n: 'map.png')
    print("解密角色图片中...")
    copyfiles(adv_dir, os.path.join(out_dir, 'chara'),
            lambda n: n.startswith('adv_chara'),
            decrypt=decrypt, tranformer=lambda n: n+'.png')
    print("生成对话框中...")
    image_dir = os.path.join(out_dir, 'image')
    os.makedirs(image_dir, exist_ok=True)
    with open(os.path.join(root_dir, 'download', 'rest', 'que_adv'), 'rb') as f:
        img = decrypt(f.read())
        build_que_adv(img, os.path.join(image_dir, 'que_adv.png'))
    voice_dir = os.path.join(root_dir, 'download', 'voice')
    if os.path.isdir(voice_dir):
        print("复制语音目录中...")
        copytree(voice_dir, os.path.join(out_dir, 'voice'))
    else:
        print("语音目录不存在，已忽略")


if __name__ == '__main__':
    root_dir = 'save'
    build_viewer_data(root_dir, 'viewer/js/madb.js', 'MA_DB')
    build_viewer_face(root_dir, 'viewer/image/face')
    build_viewer_card(root_dir, 'viewer/image/card')
    build_ons_data(root_dir, 'ons')
