document.addEventListener('DOMContentLoaded', () => {
    // 连接Socket.IO
    const socket = io();
    
    // 获取DOM元素
    const usernameInput = document.getElementById('username-input');
    const roomCodeInput = document.getElementById('room-code-input');
    const createRoomBtn = document.getElementById('create-room-btn');
    const joinRoomBtn = document.getElementById('join-room-btn');
    const loginArea = document.getElementById('login-area');
    const roomArea = document.getElementById('room-area');
    const gameArea = document.getElementById('game-area');
    const roomCodeDisplay = document.getElementById('room-code-display');
    const playerList = document.getElementById('player-list');
    const readyBtn = document.getElementById('ready-btn');
    const startGameBtn = document.getElementById('start-game-btn');
    const multiplayerGuessInput = document.getElementById('multiplayer-guess-input');
    const multiplayerSubmitGuess = document.getElementById('multiplayer-submit-guess');
    const multiplayerSearchResults = document.getElementById('multiplayer-search-results');
    const multiplayerGuessesContainer = document.getElementById('multiplayer-guesses-container');
    const resultModal = document.getElementById('multiplayer-result-modal');
    const closeResultModal = document.querySelector('.multiplayer-close');
    const answerInfo = document.getElementById('multiplayer-answer-info');
    const resultsTable = document.getElementById('multiplayer-results-table');
    const unreadyBtn = document.getElementById('unready-btn');
    const restartBtn = document.getElementById('restart-btn');
    const errorModal = document.getElementById('error-modal');
    const errorMessage = document.getElementById('error-message');
    const closeErrorModal = document.querySelector('.error-close');
    
    // 游戏状态
    let isHost = false;
    let isReady = false;
    let username = '';
    let roomCode = '';
    let gameStarted = false;
    let currentPlayers = [];
    let currentHost = '';
    let readyStatus = {};
    
    // 表格列名
    const tableColumns = ['代号', '英文代号', '职业', '星级', '所属阵营', '出身地', '种族', '位置', 'tag'];
    
    // 创建预设表格 - 修改表格结构
    function createGuessTable() {
        const table = document.createElement('table');
        table.className = 'guess-table';
        table.id = 'multiplayer-guess-table';
        
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        tableColumns.forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        const tbody = document.createElement('tbody');
        tbody.id = 'multiplayer-guess-table-body';
        table.appendChild(tbody);
        
        return table;
    }
    
    // 创建房间
    createRoomBtn.addEventListener('click', () => {
        if (!validateUsername()) return;
        
        username = usernameInput.value.trim();
        socket.emit('create_room', { username });
    });
    
    // 加入房间
    joinRoomBtn.addEventListener('click', () => {
        if (!validateUsername()) return;
        if (!validateRoomCode()) return;
        
        username = usernameInput.value.trim();
        roomCode = roomCodeInput.value.trim();
        socket.emit('join_room', { username, room_code: roomCode });
    });
    
    // 验证用户名
    function validateUsername() {
        const username = usernameInput.value.trim();
        if (!username) {
            showError('请输入用户名');
            return false;
        }
        return true;
    }
    
    // 验证房间号
    function validateRoomCode() {
        const roomCode = roomCodeInput.value.trim();
        if (!roomCode) {
            showError('请输入房间号');
            return false;
        }
        return true;
    }
    
    // 房间创建成功
    socket.on('room_created', (data) => {
        isHost = true;
        roomCode = data.room_code;
        username = usernameInput.value.trim();
        setupRoom(data);
    });
    
    // 加入房间成功
    socket.on('room_joined', (data) => {
        isHost = data.is_host;
        roomCode = data.room_code;
        username = usernameInput.value.trim();
        setupRoom(data);
    });
    
    // 设置房间
    function setupRoom(data) {
        loginArea.classList.add('hidden');
        roomArea.classList.remove('hidden');
        roomCodeDisplay.textContent = data.room_code;
        
        // 保存当前房间信息
        currentPlayers = data.players || [];
        currentHost = data.host || '';
        readyStatus = data.ready_status || {};
        
        // 更新玩家列表和准备状态
        updatePlayerList();
        
        // 如果是房主，隐藏准备按钮，房主默认准备
        if (isHost) {
            readyBtn.classList.add('hidden');
            startGameBtn.classList.remove('hidden');
        } else {
            readyBtn.classList.remove('hidden');
            startGameBtn.classList.add('hidden');
            
            // 设置初始准备状态
            isReady = readyStatus[username] || false;
            readyBtn.textContent = isReady ? '取消准备' : '准备';
            readyBtn.className = isReady ? 'ready' : 'not-ready';
        }
    }
    
    // 更新玩家列表，显示准备状态
    function updatePlayerList() {
        playerList.innerHTML = '';
        
        currentPlayers.forEach(player => {
            const li = document.createElement('li');
            li.className = 'player-item';
            
            // 创建玩家名称部分
            const nameSpan = document.createElement('span');
            nameSpan.textContent = player;
            nameSpan.className = 'player-name';
            li.appendChild(nameSpan);
            
            // 添加房主标签
            if (player === currentHost) {
                const hostBadge = document.createElement('span');
                hostBadge.textContent = '房主';
                hostBadge.className = 'host-badge';
                li.appendChild(hostBadge);
            } 
            // 非房主显示准备状态
            else if (player in readyStatus) {
                const readyBadge = document.createElement('span');
                readyBadge.textContent = readyStatus[player] ? '已准备' : '未准备';
                readyBadge.className = readyStatus[player] ? 'ready-badge' : 'not-ready-badge';
                li.appendChild(readyBadge);
            }
            
            playerList.appendChild(li);
        });
    }

    // 玩家加入房间
    socket.on('player_joined', (data) => {
        currentPlayers = data.players || [];
        currentHost = data.host || '';
        readyStatus = data.ready_status || {};
        updatePlayerList();
        
        // 显示通知
        console.log(`${data.username} 加入了房间`);
    });
    
    // 玩家离开房间
    socket.on('player_left', (data) => {
        currentPlayers = data.players || [];
        currentHost = data.host || '';
        updatePlayerList();
        
        // 如果当前玩家变成房主
        if (username === data.host && !isHost) {
            isHost = true;
            readyBtn.classList.add('hidden');
            startGameBtn.classList.remove('hidden');
        }
        
        // 显示通知
        console.log(`${data.username} 离开了房间`);
    });
    
    // 准备/取消准备按钮
    readyBtn.addEventListener('click', () => {
        socket.emit('toggle_ready', {});
    });
    
    // 更新准备状态
    socket.on('ready_status_update', (data) => {
        console.log("收到准备状态更新:", data.ready_status);
        
        // 更新准备状态
        readyStatus = data.ready_status || {};
        
        // 更新自己的准备状态UI
        if (username in readyStatus) {
            isReady = readyStatus[username];
            readyBtn.textContent = isReady ? '取消准备' : '准备';
            readyBtn.className = isReady ? 'ready' : 'not-ready';
        }
        
        // 更新玩家列表中所有玩家的准备状态
        updatePlayerList();
    });
    
    // 开始游戏
    startGameBtn.addEventListener('click', () => {
        socket.emit('start_game');
    });
    
    // 游戏开始
    socket.on('game_started', (data) => {
        roomArea.classList.add('hidden');
        gameArea.classList.remove('hidden');
        gameStarted = true;
        
        // 创建猜测表格
        multiplayerGuessesContainer.innerHTML = '';
        multiplayerGuessesContainer.appendChild(createGuessTable());
    });
    
    // 搜索角色
    multiplayerGuessInput.addEventListener('input', async (e) => {
        const query = e.target.value.trim();
        if (query.length < 1) {
            multiplayerSearchResults.innerHTML = '';
            return;
        }

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();
            displaySearchResults(data.results);
        } catch (error) {
            console.error('Error searching:', error);
        }
    });

    // 显示搜索结果
    function displaySearchResults(results) {
        multiplayerSearchResults.innerHTML = '';
        if (results.length === 0) {
            return;
        }

        const ul = document.createElement('ul');
        ul.className = 'search-results-list';
        
        results.forEach(character => {
            const li = document.createElement('li');
            li.textContent = `${character['代号']} (${character['英文代号']})`;
            li.addEventListener('click', () => {
                multiplayerGuessInput.value = character['代号'];
                multiplayerSearchResults.innerHTML = '';
                submitGuess(character['代号']);
            });
            ul.appendChild(li);
        });
        
        multiplayerSearchResults.appendChild(ul);
    }

    // 提交猜测
    function submitGuess(guess) {
        socket.emit('make_guess', { code: guess });
        multiplayerGuessInput.value = '';
    }

    multiplayerSubmitGuess.addEventListener('click', () => {
        const guess = multiplayerGuessInput.value.trim();
        if (guess) {
            submitGuess(guess);
        }
    });
    
    // 显示猜测结果 - 仅显示当前用户的猜测结果
    socket.on('guess_result', (data) => {
        // 只处理当前用户自己的猜测
        if (data.username === username) {
            displayGuess(data.guessed_character, data.similarities);
        }
    });

    // 显示猜测结果 - 修复表格错位问题
    function displayGuess(character, similarities) {
        // 获取表格或创建一个（如果不存在）
        let tbody = document.getElementById('multiplayer-guess-table-body');
        if (!tbody) {
            const table = createGuessTable();
            multiplayerGuessesContainer.appendChild(table);
            tbody = document.getElementById('multiplayer-guess-table-body');
        }
        
        // 创建数据行
        const dataRow = document.createElement('tr');
        
        // 填充每一列的数据
        tableColumns.forEach(key => {
            const td = document.createElement('td');
            
            // 处理职业和子职业合并
            if (key === '职业') {
                td.textContent = `${character['职业']}-${character['子职业']}`;
                // 使用子职业的相似度来决定背景色
                if (similarities['职业'] === 'green' && similarities['子职业'] === 'green') {
                    td.classList.add('green-bg');
                } else if (similarities['职业'] === 'green' || similarities['子职业'] === 'yellow') {
                    td.classList.add('yellow-bg');
                }
            } else {
                td.textContent = character[key] || '';
                if (similarities[key] === 'green') {
                    td.classList.add('green-bg');
                } else if (similarities[key] === 'yellow') {
                    td.classList.add('yellow-bg');
                }
            }
            dataRow.appendChild(td);
        });
        
        tbody.appendChild(dataRow);
    }
    
    // 游戏结束
    socket.on('game_over', (data) => {
        gameStarted = false;
        
        // 显示结果模态框
        answerInfo.innerHTML = `
            <h3>正确答案是：${data.answer['代号']}</h3>
            <p>英文代号：${data.answer['英文代号']}</p>
            <p>职业：${data.answer['职业']}-${data.answer['子职业']}</p>
            <p>星级：${data.answer['星级']}</p>
            <p>所属阵营：${data.answer['所属阵营']}</p>
            <p>出身地：${data.answer['出身地']}</p>
            <p>种族：${data.answer['种族']}</p>
            <p>位置：${data.answer['位置']}</p>
            <p>tag：${data.answer['tag']}</p>
        `;
        
        // 生成结果表格
        generateResultsTable(data.results, data.winner);
        
        // 显示重新开始按钮
        if (isHost) {
            restartBtn.classList.remove('hidden');
        } else {
            restartBtn.classList.add('hidden');
        }
        
        resultModal.style.display = 'block';
    });
    
    // 生成结果表格
    function generateResultsTable(results, winner) {
        resultsTable.innerHTML = '';
        
        // 创建表头
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        // 添加回合列
        const roundHeader = document.createElement('th');
        roundHeader.textContent = '回合';
        headerRow.appendChild(roundHeader);
        
        // 为每个玩家添加一列
        Object.keys(results).forEach(player => {
            const th = document.createElement('th');
            th.textContent = player;
            if (player === winner) {
                th.style.color = 'green';
                th.style.fontWeight = 'bold';
            }
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        resultsTable.appendChild(thead);
        
        // 创建表体
        const tbody = document.createElement('tbody');
        
        // 找出最大回合数
        let maxRounds = 0;
        Object.values(results).forEach(playerResults => {
            maxRounds = Math.max(maxRounds, playerResults.length);
        });
        
        // 为每个回合创建一行
        for (let i = 0; i < maxRounds; i++) {
            const row = document.createElement('tr');
            
            // 添加回合数
            const roundCell = document.createElement('td');
            roundCell.textContent = i + 1;
            row.appendChild(roundCell);
            
            // 为每个玩家添加单元格
            Object.keys(results).forEach(player => {
                const td = document.createElement('td');
                if (i < results[player].length) {
                    const guess = results[player][i];
                    td.textContent = guess.character_id;
                    
                    if (guess.correct) {
                        td.innerHTML += ' ✅';
                        td.classList.add('correct-guess');
                    } else {
                        td.innerHTML += ' ❌';
                    }
                }
                row.appendChild(td);
            });
            
            tbody.appendChild(row);
        }
        
        resultsTable.appendChild(tbody);
    }
    
    // 取消准备按钮
    unreadyBtn.addEventListener('click', () => {
        socket.emit('toggle_ready', {});  // 同样发送空对象
    });
    
    // 重新开始游戏
    restartBtn.addEventListener('click', () => {
        socket.emit('start_game');
        resultModal.style.display = 'none';
    });
    
    // 关闭结果模态框
    closeResultModal.addEventListener('click', () => {
        resultModal.style.display = 'none';
        roomArea.classList.remove('hidden');
        gameArea.classList.add('hidden');
    });
    
    // 显示错误信息
    function showError(message) {
        errorMessage.textContent = message;
        errorModal.style.display = 'block';
    }
    
    // Socket错误处理
    socket.on('error', (data) => {
        showError(data.message);
    });
    
    // 关闭错误模态框
    closeErrorModal.addEventListener('click', () => {
        errorModal.style.display = 'none';
    });
    
    // 点击模态框外部关闭
    window.addEventListener('click', (event) => {
        if (event.target === errorModal) {
            errorModal.style.display = 'none';
        }
        if (event.target === resultModal && !gameStarted) {
            resultModal.style.display = 'none';
            roomArea.classList.remove('hidden');
            gameArea.classList.add('hidden');
        }
    });
    
    // 离开页面时断开连接
    window.addEventListener('beforeunload', () => {
        socket.emit('leave_room');
    });
});
