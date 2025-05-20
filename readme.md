# 蒂一把——明日方舟猜角色
<p align="center">
    <img src="static/image/115411988_p13.jpg" width="300"><br>
</p>

> 灵感来源：[Blast](https://blast.tv/counter-strikle), [二次元猜角色](https://anime-character-guessr.netlify.app/)
数据来源：明日方舟，[PRTS](https://prts.wiki)

## 前言
目前算是结项了，后续应该不会再有大更新，只会添加新的干员信息了。
很遗憾，最后还是没有彻底战胜在服务器上多人游戏卡顿的问题。虽然后面用上了使用了Redis做会话管理，但是在阿里云2g2c的服务器上玩的人多了还是会卡得很。所以如果想玩的话还是推荐玩单人模式，如果服务器还没过期的话可以直接点下面的网址体验。
干员头像算是弃坑了，即使后续更新出这个内容也不会是我更新了，果咩。
这是自己第一次进行整个项目的vibe coding，大部分代码由copilot生成。我自己其实根本不懂前后端相关的知识，但是还是完成了这样一个项目，切实体会到了“现代”编程有多轻松，感谢copilot🙏。（其实最开始是打算用cursor的，但是没米qwq）
当然，虽然已经结项了，本项目仍然欢迎提issue反馈bug，只是不一定有时间改。直接提交pr依旧是欢迎的。
最后，玩的开心！
——Dioxane, 2025.5.20
## 规则
- 点击`开始新游戏`开始游戏，系统将从数据库中随机选择一个谜底干员。
- 在输入框输入目标干员中文或英文id的部分，在搜索推荐框中选择目标干员。
- 每次猜测后会出现一行信息表示你本次猜测干员的各个信息与谜底干员相关信息的差异程度。绿色是完全符合，黄色是部分符合，白色是完全不符。职业黄色代表大职业正确，小分支错误；阵营黄色代表父阵营正确，子阵营错误；tag黄色代表至少有一个tag符合但tag不完全符合。
- 每轮游戏总共有十次猜测机会，若猜对干员或十次机会后仍未猜对则本轮游戏结束并公布正确谜底干员。
- 玩的开心！🧸

## 目前已支持
- 可以在[这个网址](https://guessr.parodydeepseek.news/)在线尝试本游戏了🎉
- 可以自己部署在自己的服务器上游玩。因为上面的网站服务器流量有限所以大家轻点造，想长久体验推荐还是自己部署。
- 全角色均已支持，可在本地部署环境后本机游玩。
- 在一台电脑上启动网页服务后局域网内设备游玩。


## 本地安装指南&如何使用
1. 创建一个Python虚拟环境并切换到虚拟环境中(已在Python3.9.6下验证)
2. 按顺序执行以下代码
```bash
git clone https://github.com/Dioxane123/Arknights_guessr.git
pip install -r requirments.txt
```
3. 启动flask服务
```bash
python main.py
```
4. 打开浏览器并[访问本机12920端口](locohost:12920)

## 服务器上部署安装教程(简洁版)
1. 准备一台服务器，确认80与443端口对外开放。
2. 配置Redis服务器，本项目使用的Redis数据库端口为默认的6379，具体使用DB为0号，如果有需求可以在`app.py`文件内自行修改相关配置。
3. 配置Apache2环境。
```bash
sudo apt update
sudo apt install apache2 -y
```
4. 将本项目clone到默认路径下。
```bash
sudo git clone https://github.com/Dioxane123/Arknights_guessr.git ~/flaskapp
```
5. 在用户目录中创建一个虚拟环境并安装所需包。
```bash
cd ~
mkdir guessr
python3 -m venv guessr
source guessr/activate/bin
pip install -r /var/www/flaskapp/requirements.txt
```
6. 修改apache配置文件，将`flaskapp.conf`的ServerName对应值修改为你的域名或者服务器ip，并执行以下命令移动配置文件。
```bash
sudo mv ~/flaskapp.conf /etc/apache2/sites-available
```
7. 启用站点
```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
sudo a2ensite /etc/apache2/sites0available/flaskapp.conf
sudo systemctl restart apache2
```
8. 启动服务端
请使用systemctl, supervisor等方法执行项目文件夹中的start_server.sh并保持持续执行。
```bash
bash start_server.sh
```
9.  现在应该已经成功部署了，可以打开浏览器测试了！🥳
- 关于证书等等问题可以找其他教程或者直接问大模型，大模型确实好用啊👍

## 未来更新计划
- [x] 完成数据库（截至2025.5）。
- [x] 支持部署在服务器上。
- [x] 优化展示表格，在手机上能正常使用。
- [ ] 表格展示干员头像。
- [x] 支持本地多人在线对战。
- [x] 支持服务器多人在线对战。
### 欢迎任何issue，有任何修改建议或者bug修正请直接提pr😘。

> 头图来源：是屑天痕([pixiv](https://www.pixiv.net/users/80625765), [bilibili](https://space.bilibili.com/277914153))，温蒂可爱捏.