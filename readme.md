# 蒂一把——明日方舟猜角色
> 灵感来源：[Blast](https://blast.tv/counter-strikle), [二次元猜角色](https://anime-character-guessr.netlify.app/)

> 数据来源：明日方舟，[PRTS](https://prts.wiki)

## 前言
晚点再写，反正刚创仓库没人看。🫥

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
2. 配置Apache2环境。
```bash
sudo apt update
sudo apt install apache2 -y
```
3. 将本项目clone到/var/www/flaskapp路径下。
```bash
sudo git clone https://github.com/Dioxane123/Arknights_guessr.git /var/www/flaskapp
```
4. 在用户目录中创建一个虚拟环境并安装所需包。
```bash
cd ~
mkdir guessr
python3 -m venv guessr
source guessr/activate/bin
pip install -r /var/www/flaskapp/requirements.txt
```
5. 修改apache配置文件，将`flaskapp.conf`的ServerName对应值修改为你的域名或者服务器ip，并执行以下命令移动配置文件。
```bash
sudo mv /var/www/flaskapp/flaskapp.conf /etc/apache2/sites-available
```
6. 启用站点
```bash
sudo a2enmod wsgi
sudo a2ensite /etc/apache2/sites0available/flaskapp.conf
sudo systemctl reload apache2
```
7. 现在应该已经成功部署了，可以打开浏览器测试了！🥳
- 关于证书等等问题可以找其他教程或者直接问大模型，大模型确实好用啊👍

## 未来更新计划
- [x] 完成数据库。
- [x] 支持部署在服务器上。
- [x] 优化展示表格，在手机上能正常使用。
- [ ] 表格展示干员头像。
- [ ] 支持多人在线对战。
### 欢迎任何issue，有任何修改建议或者bug修正请直接提pr😘。
<p align="center">
    <img src="static/image/115411988_p13.jpg" width="300"><br>
    <span style="font-size: 8px; color: gray;">
        图片来源：
        <a herf="https://www.pixiv.net/users/80625765">
        是屑天痕
        </a>
        ，温蒂可爱捏。
    </span>
</p>