const API_URL = "http://localhost:8000";
let sessionId = null;
let chatHistory = [];

// DOM Elements
const pdfUpload = document.getElementById('pdf-upload');
const processBtn = document.getElementById('process-btn');
const fileList = document.getElementById('file-list');
const dropzone = document.getElementById('dropzone');

const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatHistoryContainer = document.getElementById('chat-history');

const summarizeBtn = document.getElementById('summarize-btn');
const quizBtn = document.getElementById('quiz-btn');

const chatView = document.getElementById('chat-view');
const summaryView = document.getElementById('summary-view');
const quizView = document.getElementById('quiz-view');

const backToChatSum = document.getElementById('back-to-chat-sum');
const backToChatQuiz = document.getElementById('back-to-chat-quiz');

// Event Listeners
pdfUpload.addEventListener('change', (e) => {
    const files = e.target.files;
    fileList.innerHTML = '';
    for (let i = 0; i < files.length; i++) {
        const div = document.createElement('div');
        div.textContent = `📄 ${files[i].name}`;
        fileList.appendChild(div);
    }
});

processBtn.addEventListener('click', async () => {
    const files = pdfUpload.files;
    if (files.length === 0) {
        alert("Please select at least one PDF.");
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    const originalText = processBtn.textContent;
    processBtn.textContent = "Processing...";
    processBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (response.ok) {
            sessionId = data.session_id;
            alert("Documents Processed Successfully!");
            chatInput.disabled = false;
            sendBtn.disabled = false;
            summarizeBtn.disabled = false;
            quizBtn.disabled = false;
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (error) {
        console.error("Error uploading files:", error);
        alert("Failed to connect to backend server.");
    } finally {
        processBtn.textContent = originalText;
        processBtn.disabled = false;
    }
});

function appendMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? '🧑‍💻' : '🧠';
    
    const text = document.createElement('div');
    text.className = 'message-content';
    text.textContent = content; // Using textContent to avoid XSS
    
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(text);
    chatHistoryContainer.appendChild(msgDiv);
    
    // Auto scroll
    chatHistoryContainer.scrollTop = chatHistoryContainer.scrollHeight;
}

sendBtn.addEventListener('click', async () => {
    const query = chatInput.value.trim();
    if (!query || !sessionId) return;

    // Show user msg
    appendMessage('user', query);
    chatInput.value = '';
    chatInput.disabled = true;
    sendBtn.disabled = true;

    // Call API
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                query: query,
                history: chatHistory
            })
        });
        const data = await response.json();
        
        if (response.ok) {
            appendMessage('assistant', data.answer);
            chatHistory.push({ role: 'user', content: query });
            chatHistory.push({ role: 'assistant', content: data.answer });
        } else {
            appendMessage('assistant', `Error: ${data.detail}`);
        }
    } catch (error) {
        console.error(error);
        appendMessage('assistant', "Failed to connect to backend server.");
    } finally {
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendBtn.click();
});

// View Navigation
function switchView(viewId) {
    document.querySelectorAll('.view-container').forEach(el => el.classList.remove('active', 'hidden'));
    document.querySelectorAll('.view-container').forEach(el => {
        if (el.id === viewId) el.classList.add('active');
        else el.classList.add('hidden');
    });
}

backToChatSum.addEventListener('click', () => switchView('chat-view'));
backToChatQuiz.addEventListener('click', () => switchView('chat-view'));

summarizeBtn.addEventListener('click', async () => {
    if (!sessionId) {
        alert("Please process a document first.");
        return;
    }
    switchView('summary-view');
    const summaryText = document.getElementById('summary-text');
    const loader = document.querySelector('#summary-content .loader');
    
    summaryText.innerHTML = '';
    loader.classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/summarize/${sessionId}`);
        const data = await response.json();
        
        if (response.ok) {
            // Split by newlines and create list or paragraphs
            const lines = data.summary.split('\n').filter(l => l.trim().length > 0);
            const ul = document.createElement('ul');
            lines.forEach(line => {
                const li = document.createElement('li');
                li.textContent = line.replace(/^- /, '').trim();
                ul.appendChild(li);
            });
            summaryText.appendChild(ul);
        } else {
            summaryText.textContent = `Error: ${data.detail}`;
        }
    } catch (error) {
        console.error(error);
        summaryText.textContent = "Failed to fetch summary.";
    } finally {
        loader.classList.add('hidden');
    }
});

quizBtn.addEventListener('click', async () => {
    if (!sessionId) {
        alert("Please process a document first.");
        return;
    }
    switchView('quiz-view');
    const quizQuestions = document.getElementById('quiz-questions');
    const loader = document.querySelector('#quiz-content .loader');
    
    quizQuestions.innerHTML = '';
    loader.classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/quiz/${sessionId}`);
        const data = await response.json();
        
        if (response.ok) {
            data.quiz.forEach((q, idx) => {
                const item = document.createElement('div');
                item.className = 'quiz-item';
                
                const question = document.createElement('div');
                question.className = 'quiz-question';
                question.textContent = `Q${idx + 1}: ${q.question}`;
                
                const showAnsBtn = document.createElement('button');
                showAnsBtn.className = 'quiz-answer-btn';
                showAnsBtn.textContent = 'Show Answer';
                
                const answerContent = document.createElement('div');
                answerContent.className = 'quiz-answer-content hidden';
                
                const ansStr = document.createElement('p');
                ansStr.innerHTML = `<strong>Answer:</strong> ${q.answer}`;
                answerContent.appendChild(ansStr);
                
                if (q.explanation) {
                    const expStr = document.createElement('p');
                    expStr.innerHTML = `<em>Explanation:</em> ${q.explanation}`;
                    answerContent.appendChild(expStr);
                }
                
                showAnsBtn.addEventListener('click', () => {
                    answerContent.classList.toggle('hidden');
                    showAnsBtn.textContent = answerContent.classList.contains('hidden') ? 'Show Answer' : 'Hide Answer';
                });
                
                item.appendChild(question);
                item.appendChild(showAnsBtn);
                item.appendChild(answerContent);
                quizQuestions.appendChild(item);
            });
        } else {
            quizQuestions.textContent = `Error: ${data.detail}`;
        }
    } catch (error) {
        console.error(error);
        quizQuestions.textContent = "Failed to fetch quiz.";
    } finally {
        loader.classList.add('hidden');
    }
});

// Initial state
summarizeBtn.disabled = true;
quizBtn.disabled = true;
