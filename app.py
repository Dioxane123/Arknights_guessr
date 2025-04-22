from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import os
import uuid
import time
from game_logic import (
    load_character_data, convert_to_chinese_fields, compare_characters, 
    generate_room_code
)

app = Flask(__name__)
# 设置一个密钥用于会话加密
app.secret_key = os.environ.get('SECRET_KEY', 'arknights_guessr_secret')
socketio = SocketIO(app, cors_allowed_origins="*")

# 房间管理
rooms = {}

# 获取当前用户的游戏状态
def get_user_game_state():
    # 确保用户有会话ID
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    # 如果会话中没有游戏状态，创建一个新的
    if 'game_state' not in session:
        session['game_state'] = {
            'current_answer': None,
            'guesses': [],
            'max_guesses': 10
        }
    
    return session['game_state']

# 更新用户游戏状态
def update_user_game_state(game_state):
    session['game_state'] = game_state
    # 确保会话被保存
    session.modified = True

# 路由：首页
@app.route('/')
def index():
    return render_template('index.html')

# 路由：模式选择
@app.route('/mode_selection')
def mode_selection():
    return render_template('mode_selection.html')

# 路由：单人模式
@app.route('/singleplayer')
def singleplayer():
    return render_template('index.html')

# 路由：多人模式
@app.route('/multiplayer')
def multiplayer():
    return render_template('multiplayer.html')

# 路由：开始游戏
@app.route('/start_game', methods=['POST'])
def start_game():
    characters = load_character_data()
    game_state = get_user_game_state()
    game_state['current_answer'] = random.choice(characters)
    game_state['guesses'] = []
    update_user_game_state(game_state)
    return jsonify({'status': 'success'})

# 路由：搜索角色
@app.route('/search', methods=['POST'])
def search_character():
    query = request.json.get('query', '').lower()
    characters = load_character_data()
    
    results = [char for char in characters if query in str(char['id']).lower() or query in str(char['En_id']).lower()]
    
    # 转换结果为前端需要的格式
    converted_results = [convert_to_chinese_fields(char) for char in results]
    
    return jsonify({'results': converted_results[:10]})  # 限制结果数量

# 路由：进行猜测
@app.route('/guess', methods=['POST'])
def make_guess():
    guess_code = request.json.get('code')
    characters = load_character_data()
    
    # 获取当前用户的游戏状态
    game_state = get_user_game_state()
    
    # 确保游戏已经开始
    if not game_state['current_answer']:
        return jsonify({'error': '请先开始游戏'})
    
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
    
    # 更新游戏状态
    update_user_game_state(game_state)
    
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

# SocketIO事件：创建房间
@socketio.on('create_room')
def on_create_room(data):
    username = data['username']
    # 生成房间号
    room_code = generate_room_code()
    while room_code in rooms:
        room_code = generate_room_code()
    
    # 创建房间 - 房主默认已准备
    rooms[room_code] = {
        'players': {username: {'ready': True, 'is_host': True, 'guesses': []}},  # 设置房主默认已准备
        'game_started': False,
        'current_answer': None,
        'host': username
    }
    
    # 将用户加入Socket.IO房间
    session['room'] = room_code
    session['username'] = username
    join_room(room_code)
    
    # 返回房间信息，包含所有玩家准备状态
    ready_status = {player: info['ready'] for player, info in rooms[room_code]['players'].items()}
    emit('room_created', {
        'room_code': room_code, 
        'players': list(rooms[room_code]['players'].keys()), 
        'is_host': True, 
        'host': username,
        'ready_status': ready_status
    })

# SocketIO事件：加入房间
@socketio.on('join_room')
def on_join_room(data):
    username = data['username']
    room_code = data['room_code']
    
    if room_code not in rooms:
        emit('error', {'message': '房间不存在'})
        return
    
    # 检查游戏是否已经开始
    if rooms[room_code]['game_started']:
        emit('error', {'message': '游戏已经开始，无法加入'})
        return
    
    # 检查用户名是否已存在
    if username in rooms[room_code]['players']:
        emit('error', {'message': '该用户名已被使用'})
        return
    
    # 将用户加入房间
    rooms[room_code]['players'][username] = {'ready': False, 'is_host': False, 'guesses': []}
    
    # 将用户加入Socket.IO房间
    session['room'] = room_code
    session['username'] = username
    join_room(room_code)
    
    # 通知房间内所有人有新玩家加入，包含准备状态
    ready_status = {player: info['ready'] for player, info in rooms[room_code]['players'].items()}
    emit('player_joined', {
        'username': username, 
        'players': list(rooms[room_code]['players'].keys()),
        'host': rooms[room_code]['host'],
        'ready_status': ready_status
    }, room=room_code)
    
    # 返回房间信息给新加入的玩家，包含准备状态
    emit('room_joined', {
        'room_code': room_code,
        'players': list(rooms[room_code]['players'].keys()),
        'host': rooms[room_code]['host'],
        'is_host': False,
        'ready_status': ready_status
    })

# SocketIO事件：切换准备状态
@socketio.on('toggle_ready')
def on_toggle_ready(data=None):  # 修改这里，让data参数成为可选的
    username = session.get('username')
    room_code = session.get('room')
    
    if not username or not room_code or room_code not in rooms or username not in rooms[room_code]['players']:
        return
    
    # 切换准备状态
    current_ready = rooms[room_code]['players'][username]['ready']
    rooms[room_code]['players'][username]['ready'] = not current_ready
    
    # 广播新的准备状态
    ready_status = {player: info['ready'] for player, info in rooms[room_code]['players'].items()}
    emit('ready_status_update', {'ready_status': ready_status}, room=room_code)

# SocketIO事件：开始游戏
@socketio.on('start_game')
def on_start_game():
    username = session.get('username')
    room_code = session.get('room')
    
    if not username or not room_code or room_code not in rooms:
        return
    
    # 检查是否是房主
    if rooms[room_code]['host'] != username:
        emit('error', {'message': '只有房主可以开始游戏'})
        return
    
    # 检查是否有足够的玩家
    if len(rooms[room_code]['players']) < 2:
        emit('error', {'message': '至少需要2名玩家才能开始游戏'})
        return
    
    # 检查其他玩家是否都已准备
    all_ready = all(info['ready'] for player, info in rooms[room_code]['players'].items() if player != username)
    if not all_ready:
        emit('error', {'message': '有玩家尚未准备'})
        return
    
    # 开始游戏
    characters = load_character_data()
    rooms[room_code]['current_answer'] = random.choice(characters)
    rooms[room_code]['game_started'] = True
    
    # 清空所有玩家的猜测记录
    for player in rooms[room_code]['players']:
        rooms[room_code]['players'][player]['guesses'] = []
    
    # 广播游戏开始
    emit('game_started', {}, room=room_code)

# SocketIO事件：进行猜测
@socketio.on('make_guess')
def on_make_guess(data):
    guess_code = data['code']
    username = session.get('username')
    room_code = session.get('room')
    
    if not username or not room_code or room_code not in rooms:
        emit('error', {'message': '房间不存在'})
        return
    
    # 检查游戏是否已开始
    if not rooms[room_code]['game_started']:
        emit('error', {'message': '游戏尚未开始'})
        return
    
    characters = load_character_data()
    
    # 查找猜测的角色
    guessed_character = next((char for char in characters if char['id'] == guess_code), None)
    if not guessed_character:
        emit('error', {'message': '角色不存在'})
        return
    
    # 比较相似度
    similarities = compare_characters(guessed_character, rooms[room_code]['current_answer'])
    
    # 转换为前端需要的格式
    converted_character = convert_to_chinese_fields(guessed_character)
    
    # 记录猜测
    guess_info = {
        'character': converted_character,
        'similarities': similarities,
        'is_correct': guessed_character['id'] == rooms[room_code]['current_answer']['id'],
        'timestamp': time.time()
    }
    rooms[room_code]['players'][username]['guesses'].append(guess_info)
    
    # 广播猜测结果
    emit('guess_result', {
        'username': username,
        'guessed_character': converted_character,
        'similarities': similarities,
        'is_correct': guessed_character['id'] == rooms[room_code]['current_answer']['id']
    }, room=room_code)
    
    # 检查游戏是否结束
    game_over = False
    winner = None
    is_correct = guessed_character['id'] == rooms[room_code]['current_answer']['id']
    
    if is_correct:
        game_over = True
        winner = username
    else:
        # 检查是否所有玩家都用尽次数
        max_guesses = 10
        all_used_max = True
        for player, info in rooms[room_code]['players'].items():
            if len(info['guesses']) < max_guesses:
                all_used_max = False
                break
        
        if all_used_max:
            game_over = True
    
    # 游戏结束处理
    if game_over:
        # 游戏结束，转换答案
        converted_answer = convert_to_chinese_fields(rooms[room_code]['current_answer'])
        
        # 准备结算数据
        results = {}
        for player, info in rooms[room_code]['players'].items():
            results[player] = [{'character_id': g['character']['代号'], 'correct': g['is_correct']} for g in info['guesses']]
        
        # 重置游戏状态
        rooms[room_code]['game_started'] = False
        
        # 设置所有非房主玩家为已准备状态
        host = rooms[room_code]['host']
        for player in rooms[room_code]['players']:
            if player != host:
                rooms[room_code]['players'][player]['ready'] = True
        
        # 广播游戏结束
        emit('game_over', {
            'answer': converted_answer,
            'winner': winner,
            'results': results
        }, room=room_code)
        
        # 更新房间内的准备状态
        ready_status = {player: info['ready'] for player, info in rooms[room_code]['players'].items()}
        emit('ready_status_update', {'ready_status': ready_status}, room=room_code)

# SocketIO事件：离开房间
@socketio.on('leave_room')
def on_leave_room():
    username = session.get('username')
    room_code = session.get('room')
    
    if not username or not room_code or room_code not in rooms:
        return
    
    # 离开Socket.IO房间
    leave_room(room_code)
    
    # 从房间中移除玩家
    if username in rooms[room_code]['players']:
        was_host = rooms[room_code]['players'][username]['is_host']
        del rooms[room_code]['players'][username]
        
        # 如果房间空了，删除房间
        if not rooms[room_code]['players']:
            del rooms[room_code]
            return
        
        # 如果离开的是房主，指定新房主
        if was_host:
            new_host = next(iter(rooms[room_code]['players']))
            rooms[room_code]['players'][new_host]['is_host'] = True
            rooms[room_code]['host'] = new_host
        
        # 通知房间内其他玩家
        emit('player_left', {
            'username': username, 
            'players': list(rooms[room_code]['players'].keys()),
            'host': rooms[room_code]['host']
        }, room=room_code)

# SocketIO事件：断开连接
@socketio.on('disconnect')
def on_disconnect():
    on_leave_room()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=12920)
