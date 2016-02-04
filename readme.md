# 扩散MA国服相关

国服终于关了，一些相关的纪念产物。

包含两个项目，ons为[onscripter](https://github.com/natdon/ONScripter-CN)版剧情游戏，viewer为html5版卡牌数据浏览器。

规避相关问题，版权物不予保留在仓库中。请将缓存文件(/mnt/sdcard/Android/data/com.square_enix.million_cn/files/save)复制/移动/链接到项目根目录下，并在根目录下使用`python3`运行`build.py`即可生成所需数据。

对话框图片经过截取，需要安装PIL. 不安装会忽略该文件(ons/image/que_adv.png)的生成。

如果可能，建议使用`pypy`减少运行时间。

为了生成全部剧情的脚本，需要MA缓存中保存三个势力的全部数据，即使用客户端至少登录过三个帐号，每个帐号各自完成了对应势力的全部剧情。语音文件同理。

代码很乱，有些懒得整理了。

License: [MIT License](http://www.opensource.org/licenses/mit-license.php)