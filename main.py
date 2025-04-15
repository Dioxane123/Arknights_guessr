from flask import Flask, render_template, request, jsonify
import pandas as pd
import random
import os
import json
app = Flask(__name__)

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

# 游戏状态
game_state = {
    'current_answer': None,
    'guesses': [],
    'max_guesses': 10
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    characters = load_character_data()
    game_state['current_answer'] = random.choice(characters)
    game_state['guesses'] = []
    return jsonify({'status': 'success'})

@app.route('/search', methods=['POST'])
def search_character():
    query = request.json.get('query', '').lower()
    characters = load_character_data()
    
    results = [char for char in characters if query in str(char['id']).lower() or query in str(char['En_id']).lower()]
    
    # 转换结果为前端需要的格式
    converted_results = [convert_to_chinese_fields(char) for char in results]
    
    return jsonify({'results': converted_results[:10]})  # 限制结果数量

@app.route('/guess', methods=['POST'])
def make_guess():
    guess_code = request.json.get('code')
    characters = load_character_data()
    
    # 查找猜测的角色
    guessed_character = next((char for char in characters if char['id'] == guess_code), None)
    if not guessed_character:
        return jsonify({'error': '角色不存在'})
    
    # 比较相似度
    similarities = compare_characters(guessed_character, game_state['current_answer'])
    
    # 转换为前端需要的格式
    converted_character = convert_to_chinese_fields(guessed_character)
    
    # 记录猜测
    game_state['guesses'].append({
        'character': converted_character,
        'similarities': similarities
    })
    
    # 检查是否猜中
    is_correct = guessed_character['id'] == game_state['current_answer']['id']
    game_over = is_correct or len(game_state['guesses']) >= game_state['max_guesses']
    
    # 如果游戏结束，也转换答案为前端格式
    converted_answer = convert_to_chinese_fields(game_state['current_answer']) if game_over else None
    
    return jsonify({
        'guessed_character': converted_character,
        'similarities': similarities,
        'is_correct': is_correct,
        'game_over': game_over,
        'answer': converted_answer
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' ,port=12920)
