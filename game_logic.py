import pandas as pd
import random
import json
import string

# 加载角色数据
def load_character_data():
    df = pd.read_csv('data/characters.csv')
    return df.to_dict('records')

# 加载职业数据
def load_career_data():
    with open('data/career.json', 'r') as f:
        return json.load(f)

# 加载阵营数据
def load_camp_data():
    with open('data/camp.json', 'r') as f:
        return json.load(f)

# 添加字段映射
field_mapping = {
    'id': '代号',
    'En_id': '英文代号',
    'career': '职业',
    'subcareer': '子职业',
    'star': '星级',
    'subcamp': '所属阵营',
    'tag1': 'tag',
    'origin': '出身地',
    'species': '种族',
    'position': '位置'
}

# 将英文字段名转换为中文字段名
def convert_to_chinese_fields(character):
    converted = {}
    converted['代号'] = character['id']
    converted['英文代号'] = character['En_id']
    converted['职业'] = character['career']
    converted['子职业'] = character['subcareer']
    converted['星级'] = character['star']
    converted['所属阵营'] = character['subcamp']
    converted['出身地'] = character['origin']
    converted['种族'] = character['species']
    converted['位置'] = character['position']
    
    # 合并所有tag为一个字符串
    tags = []
    for tag_key in ['tag1', 'tag2', 'tag3', 'tag4']:
        if tag_key in character and character[tag_key] and not pd.isna(character[tag_key]):
            tags.append(character[tag_key])
    converted['tag'] = '、'.join(tags) if tags else ''
    
    return converted

# 比较两个角色的相似度
def compare_characters(guess, answer):
    similarities = {}
    for key in ['id', 'En_id', 'gender', 'star', 'species', 'origin', 'position']:
        if key in guess and key in answer:
            if guess[key] == answer[key]:
                # 将英文键名转换为中文键名
                chinese_key = field_mapping.get(key, key)
                similarities[chinese_key] = 'green'
            else:
                chinese_key = field_mapping.get(key, key)
                similarities[chinese_key] = 'white'
    
    # 处理职业 
    if guess['career'] == answer['career']:
        if guess['subcareer'] == answer['subcareer']:
            similarities['职业'] = 'green'
            similarities['子职业'] = 'green'
        else:
            similarities['职业'] = 'green'
            similarities['子职业'] = 'yellow'
    else:
        similarities['职业'] = 'white'
        similarities['子职业'] = 'white'

    # 处理阵营
    if guess['camp'] == answer['camp']:
        if guess['subcamp'] == answer['subcamp']:
            similarities['所属阵营'] = 'green'
        else:
            similarities['所属阵营'] = 'yellow'
    else:
        similarities['所属阵营'] = 'white'
    
    # 处理tag
    guess_tags = [guess['tag1'], guess['tag2'], guess['tag3'], guess['tag4']]
    answer_tags = [answer['tag1'], answer['tag2'], answer['tag3'], answer['tag4']]
    guess_tags = [tag for tag in guess_tags if isinstance(tag, str)]
    answer_tags = [tag for tag in answer_tags if isinstance(tag, str)]
    
    if any(tag in answer_tags for tag in guess_tags):
        similarities['tag'] = 'yellow'  # 至少有一个tag匹配
        # 如果所有tag都匹配则为绿色
        if all(tag in answer_tags for tag in guess_tags) and all(tag in guess_tags for tag in answer_tags):
            similarities['tag'] = 'green'
    else:
        similarities['tag'] = 'white'

    return similarities

# 生成随机房间码
def generate_room_code():
    """生成10位随机房间号"""
    chars = string.ascii_letters
    return ''.join(random.choice(chars) for _ in range(10))
