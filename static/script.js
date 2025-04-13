document.addEventListener('DOMContentLoaded', () => {
    const startGameBtn = document.getElementById('startGame');
    const submitGuessBtn = document.getElementById('submitGuess');
    const guessInput = document.getElementById('guessInput');
    const guessesContainer = document.getElementById('guessesContainer');
    const resultModal = document.getElementById('resultModal');
    const closeModal = document.querySelector('.close');
    const answerInfo = document.getElementById('answerInfo');
    const searchResults = document.getElementById('searchResults');
    const guessInputContainer = document.getElementById('guessInputContainer');

    // 预设列名 - 移除子职业，因为会和职业合并
    const tableColumns = ['代号', '英文代号', '职业', '星级', '所属阵营', '出身地', '种族', 'tag'];
    
    // 创建预设表格
    function createGuessTable() {
        const table = document.createElement('table');
        table.className = 'guess-table';
        table.id = 'guessTable';
        
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
        tbody.id = 'guessTableBody';
        table.appendChild(tbody);
        
        return table;
    }

    // 开始新游戏
    startGameBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/start_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                guessesContainer.innerHTML = '';
                guessInput.value = '';
                searchResults.innerHTML = '';
                guessInputContainer.classList.remove('hidden');
                
                // 创建新的猜测表格
                guessesContainer.appendChild(createGuessTable());
            }
        } catch (error) {
            console.error('Error starting game:', error);
        }
    });

    // 搜索角色
    guessInput.addEventListener('input', async (e) => {
        const query = e.target.value.trim();
        if (query.length < 1) {
            searchResults.innerHTML = '';
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
        searchResults.innerHTML = '';
        if (results.length === 0) {
            return;
        }

        const ul = document.createElement('ul');
        ul.className = 'search-results-list';
        
        results.forEach(character => {
            const li = document.createElement('li');
            li.textContent = `${character['代号']} (${character['英文代号']})`;
            li.addEventListener('click', () => {
                guessInput.value = character['代号'];
                searchResults.innerHTML = '';
                submitGuess(character['代号']);
            });
            ul.appendChild(li);
        });
        
        searchResults.appendChild(ul);
    }

    // 提交猜测 - 修改传递正确与否参数
    async function submitGuess(guess) {
        try {
            const response = await fetch('/guess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code: guess })
            });

            const data = await response.json();
            
            if (data.error) {
                alert(data.error);
                return;
            }

            // 显示猜测结果
            displayGuess(data.guessed_character, data.similarities);

            // 如果游戏结束，显示答案
            if (data.game_over) {
                displayAnswer(data.answer, data.is_correct);
                guessInputContainer.classList.add('hidden');
            }

            guessInput.value = '';
            searchResults.innerHTML = '';
        } catch (error) {
            console.error('Error making guess:', error);
        }
    }

    submitGuessBtn.addEventListener('click', () => {
        const guess = guessInput.value.trim();
        if (guess) {
            submitGuess(guess);
        }
    });

    // 显示猜测结果
    function displayGuess(character, similarities) {
        // 获取表格或创建一个（如果不存在）
        let tbody = document.getElementById('guessTableBody');
        if (!tbody) {
            const table = createGuessTable();
            guessesContainer.appendChild(table);
            tbody = document.getElementById('guessTableBody');
        }
        
        // 创建数据行
        const dataRow = document.createElement('tr');
        
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
                td.textContent = character[key];
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

    // 显示答案 - 合并职业和子职业的展示
    function displayAnswer(answer, isCorrect) {
        const resultMessage = isCorrect ? 
            "<h2>恭喜！您成功猜出了干员！</h2>" : 
            "<h2>很遗憾，您未能猜出正确干员</h2>";
            
        answerInfo.innerHTML = `
            ${resultMessage}
            <h3>正确答案是：${answer['代号']}</h3>
            <p>英文代号：${answer['英文代号']}</p>
            <p>职业：${answer['职业']}-${answer['子职业']}</p>
            <p>星级：${answer['星级']}</p>
            <p>所属阵营：${answer['所属阵营']}</p>
            <p>出身地：${answer['出身地']}</p>
            <p>种族：${answer['种族']}</p>
            <p>tag：${answer['tag']}</p>
        `;
        resultModal.style.display = 'block';
    }

    // 关闭模态框
    closeModal.addEventListener('click', () => {
        resultModal.style.display = 'none';
    });

    // 点击模态框外部关闭
    window.addEventListener('click', (event) => {
        if (event.target === resultModal) {
            resultModal.style.display = 'none';
        }
    });
});