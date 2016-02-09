使用支持 html5 的浏览器打开 index.html 即可。

如果需要查看全尺寸卡图，请将文件解压到`image/full_cards`下。
如果是从SD服务器扒下来的，应该是这个样子的：

- viewer/image/full_cards/full_thumbnail_chara_1.png
                         /full_thumbnail_chara_1_horo.png
                         ...
卡牌头像文件来自MA国服缓存(`/mnt/sdcard/Android/data/com.square_enix.million_cn/files/save/download/image/face`)，如果你下载的精简版本，使用解密工具解密后将得到的png文件放到`image/face`下即可。
当找不到全尺寸卡图时会首先尝试使用缩略图，将`/mnt/sdcard/Android/data/com.square_enix.million_cn/files/save/download/image/card`中的文件解密后放到`image/card`下即可。