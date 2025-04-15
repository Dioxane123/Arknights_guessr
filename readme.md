# 蒂一把——明日方舟猜角色
灵感来源：[Blast](https://blast.tv/counter-strikle), [二次元猜角色](https://anime-character-guessr.netlify.app/)

数据来源：明日方舟，[PRTS](https://prts.wiki)
--
## 前言
晚点再写，反正刚创仓库没人看。

## 目前已支持
- 全角色均已支持，可在本地部署环境后本机游玩。
- 在一台电脑上启动网页服务后局域网内设备游玩。


## 安装指南&如何使用
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

## 未来更新计划
- [x] 完成数据库。
- [ ] 支持部署在服务器上。
- [ ] 优化展示表格，在手机上能正常使用。
- [ ] 表格展示干员头像。
- [ ] 支持多人在线对战。
### 欢迎任何issue，有任何修改建议或者bug修正请直接提pr😘。