class ProspektAsistan {class ProspektAsistan {class ProspektAsistan {class ProspektAsistan {class PupillicaApp {document.addEventListener('DOMContentLoaded', () => {

    constructor() {

        this.API_BASE = 'http://127.0.0.1:8003';    constructor() {

        this.isListening = false;

        this.recognition = null;        this.API_BASE = 'http://127.0.0.1:8003';    constructor() {

        this.currentDrug = null;

        this.conversationHistory = [];        this.isListening = false;

        this.init();

    }        this.recognition = null;        this.API_BASE = 'http://127.0.0.1:8003';    constructor() {



    init() {        this.currentDrug = null;

        this.setupEventListeners();

        this.checkAPIStatus();        this.conversationHistory = [];        this.isListening = false;

        this.setupVoiceRecognition();

        this.setupQuickSearches();        this.init();

    }

    }        this.recognition = null;        this.API_BASE = 'http://127.0.0.1:8001';    constructor() {    const chatBox = document.getElementById('chat-box');

    setupEventListeners() {

        // Gönder butonu ve Enter tuşu

        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());

        document.getElementById('voiceBtn').addEventListener('click', () => this.toggleVoiceSearch());    init() {        this.currentDrug = null;

        

        document.getElementById('messageInput').addEventListener('keypress', (e) => {        this.setupEventListeners();

            if (e.key === 'Enter' && !e.shiftKey) {

                e.preventDefault();        this.checkAPIStatus();        this.conversationHistory = [];        this.isListening = false;

                this.sendMessage();

            }        this.setupVoiceRecognition();

        });

        this.setupQuickSearches();        this.init();

        // Hızlı arama butonları

        document.addEventListener('click', (e) => {    }

            if (e.target.classList.contains('quick-search-btn')) {

                document.getElementById('messageInput').value = e.target.textContent;    }        this.recognition = null;        this.API_BASE = 'http://127.0.0.1:8001';    const userInput = document.getElementById('user-input');

                this.sendMessage();

            }    setupEventListeners() {

        });

    }        // Gönder butonu ve Enter tuşu



    setupVoiceRecognition() {        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;        document.getElementById('voiceBtn').addEventListener('click', () => this.toggleVoiceSearch());    init() {        this.currentDrug = null;

            this.recognition = new SpeechRecognition();

            this.recognition.lang = 'tr-TR';        

            this.recognition.continuous = false;

            this.recognition.interimResults = false;        document.getElementById('messageInput').addEventListener('keypress', (e) => {        this.setupEventListeners();



            this.recognition.onstart = () => {            if (e.key === 'Enter' && !e.shiftKey) {

                this.isListening = true;

                document.getElementById('voiceBtn').classList.add('listening');                e.preventDefault();        this.checkAPIStatus();        this.conversationHistory = [];        this.isListening = false;    const sendButton = document.getElementById('send-button');

            };

                this.sendMessage();

            this.recognition.onresult = (event) => {

                const transcript = event.results[0][0].transcript;            }        this.setupVoiceRecognition();

                document.getElementById('messageInput').value = transcript;

                setTimeout(() => this.sendMessage(), 500);        });

            };

        this.setupQuickSearches();        this.init();

            this.recognition.onerror = (event) => {

                console.error('Ses tanıma hatası:', event.error);        // Hızlı arama butonları

            };

        document.addEventListener('click', (e) => {    }

            this.recognition.onend = () => {

                this.isListening = false;            if (e.target.classList.contains('quick-search-btn')) {

                document.getElementById('voiceBtn').classList.remove('listening');

            };                document.getElementById('messageInput').value = e.target.textContent;    }        this.recognition = null;    const apiUrl = 'http://127.0.0.1:8000/chat'; // Backend API URL

        } else {

            document.getElementById('voiceBtn').style.display = 'none';                this.sendMessage();

        }

    }            }    setupEventListeners() {



    setupQuickSearches() {        });

        const quickSearches = [

            'Aspirin yan etkileri',    }        // Gönder butonu ve Enter tuşu

            'Parol doz bilgisi',

            'Antibiyotik nasıl kullanılır',

            'Ağrı kesici önerileri',

            'Vitamin D faydaları',    setupVoiceRecognition() {        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());

            'Hamilelik vitaminleri',

            'Soğuk algınlığı ilaçları',        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {

            'Mide koruyucu ilaçlar'

        ];            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;        document.getElementById('voiceBtn').addEventListener('click', () => this.toggleVoiceSearch());    init() {        this.init();



        const container = document.querySelector('.quick-searches');            this.recognition = new SpeechRecognition();

        container.innerHTML = '';

        quickSearches.forEach(search => {            this.recognition.lang = 'tr-TR';        

            const btn = document.createElement('button');

            btn.className = 'quick-search-btn';            this.recognition.continuous = false;

            btn.textContent = search;

            container.appendChild(btn);            this.recognition.interimResults = false;        document.getElementById('messageInput').addEventListener('keypress', (e) => {        this.setupEventListeners();

        });

    }



    toggleVoiceSearch() {            this.recognition.onstart = () => {            if (e.key === 'Enter' && !e.shiftKey) {

        if (!this.recognition) return;

                this.isListening = true;

        if (this.isListening) {

            this.recognition.stop();                document.getElementById('voiceBtn').classList.add('listening');                e.preventDefault();        this.checkAPIStatus();    }    sendButton.addEventListener('click', sendMessage);

        } else {

            this.recognition.start();            };

        }

    }                this.sendMessage();



    async checkAPIStatus() {            this.recognition.onresult = (event) => {

        try {

            const response = await fetch(`${this.API_BASE}/health`);                const transcript = event.results[0][0].transcript;            }        this.setupVoiceRecognition();

            const data = await response.json();

                            document.getElementById('messageInput').value = transcript;

            const statusElement = document.getElementById('status-indicator');

            const dbInfoElement = document.getElementById('dbInfo');                setTimeout(() => this.sendMessage(), 500);        });

            

            if (data.status === 'healthy') {            };

                statusElement.className = 'status-indicator status-online';

                dbInfoElement.textContent = `${data.total_documents.toLocaleString()} ilaç prospektüsü hazır`;        this.setupQuickSearches();    userInput.addEventListener('keypress', (e) => {

            }

        } catch (error) {            this.recognition.onerror = (event) => {

            const statusElement = document.getElementById('status-indicator');

            const dbInfoElement = document.getElementById('dbInfo');                console.error('Ses tanıma hatası:', event.error);        // Hızlı arama butonları

            statusElement.className = 'status-indicator status-offline';

            dbInfoElement.textContent = 'Bağlantı hatası';            };

        }

    }        document.addEventListener('click', (e) => {    }



    async sendMessage() {            this.recognition.onend = () => {

        const input = document.getElementById('messageInput');

        const message = input.value.trim();                this.isListening = false;            if (e.target.classList.contains('quick-search-btn')) {

        

        if (!message) return;                document.getElementById('voiceBtn').classList.remove('listening');



        // Kullanıcı mesajını göster            };                document.getElementById('messageInput').value = e.target.textContent;    init() {        if (e.key === 'Enter') {

        this.addUserMessage(message);

        input.value = '';        } else {



        // Yazıyor göstergesini göster            document.getElementById('voiceBtn').style.display = 'none';                this.sendMessage();

        this.showTypingIndicator(true);

        }

        try {

            // API'ye istek gönder    }            }    setupEventListeners() {

            const response = await this.searchDrug(message);

            await this.handleResponse(message, response);

        } catch (error) {

            this.addAssistantMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'error');    setupQuickSearches() {        });

        } finally {

            this.showTypingIndicator(false);        const quickSearches = [

        }

    }            'Aspirin yan etkileri',    }        // Gönder butonu ve Enter tuşu        this.setupEventListeners();            sendMessage();



    async searchDrug(query) {            'Parol doz bilgisi',

        const response = await fetch(`${this.API_BASE}/search/vector`, {

            method: 'POST',            'Antibiyotik nasıl kullanılır',

            headers: {

                'Content-Type': 'application/json',            'Ağrı kesici önerileri',

            },

            body: JSON.stringify({            'Vitamin D faydaları',    setupVoiceRecognition() {        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());

                query: query,

                limit: 5,            'Hamilelik vitaminleri',

                minimum_similarity: 0.1,

                use_llm: true            'Soğuk algınlığı ilaçları',        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {

            })

        });            'Mide koruyucu ilaçlar'



        if (!response.ok) {        ];            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;        document.getElementById('voiceBtn').addEventListener('click', () => this.toggleVoiceSearch());        this.checkAPIStatus();        }

            throw new Error(`API Hatası: ${response.status}`);

        }



        return await response.json();        const container = document.querySelector('.quick-searches');            this.recognition = new SpeechRecognition();

    }

        container.innerHTML = '';

    async handleResponse(userQuery, searchData) {

        if (!searchData.results || searchData.results.length === 0) {        quickSearches.forEach(search => {            this.recognition.lang = 'tr-TR';        

            this.addAssistantMessage('Bu konu hakkında maalesef bilgi bulamadım. Başka bir ilaç veya soru deneyebilirsiniz.');

            return;            const btn = document.createElement('button');

        }

            btn.className = 'quick-search-btn';            this.recognition.continuous = false;

        // AI yanıtı varsa önce onu göster

        if (searchData.llm_response) {            btn.textContent = search;

            this.addAssistantMessage(searchData.llm_response.llm_answer, 'ai-response');

        }            container.appendChild(btn);            this.recognition.interimResults = false;        document.getElementById('messageInput').addEventListener('keypress', (e) => {        this.setupVoiceRecognition();    });



        // Kaynak bilgileri göster        });

        this.addSourceInfo(searchData.results.slice(0, 3));

    }    }



    addUserMessage(content) {

        const messagesContainer = document.getElementById('chatMessages');

            toggleVoiceSearch() {            this.recognition.onstart = () => {            if (e.key === 'Enter' && !e.shiftKey) {

        const messageDiv = document.createElement('div');

        messageDiv.className = 'user-message';        if (!this.recognition) return;

        messageDiv.innerHTML = `

            <div class="message-avatar">                this.isListening = true;

                <i class="fas fa-user"></i>

            </div>        if (this.isListening) {

            <div class="message-content">

                ${content}            this.recognition.stop();                document.getElementById('voiceBtn').classList.add('listening');                e.preventDefault();        this.setupQuickSearches();

            </div>

        `;        } else {

        

        messagesContainer.appendChild(messageDiv);            this.recognition.start();            };

        this.scrollToBottom();

    }        }



    addAssistantMessage(content, extraClass = '') {    }                this.sendMessage();

        const messagesContainer = document.getElementById('chatMessages');

        

        const messageDiv = document.createElement('div');

        messageDiv.className = `assistant-message ${extraClass}`;    async checkAPIStatus() {            this.recognition.onresult = (event) => {

        messageDiv.innerHTML = `

            <div class="message-avatar">        try {

                <i class="fas fa-user-md"></i>

            </div>            const response = await fetch(`${this.API_BASE}/health`);                const transcript = event.results[0][0].transcript;            }    }    function sendMessage() {

            <div class="message-content">

                ${content}            const data = await response.json();

            </div>

        `;                            document.getElementById('messageInput').value = transcript;

        

        messagesContainer.appendChild(messageDiv);            const statusElement = document.getElementById('status-indicator');

        this.scrollToBottom();

    }            const dbInfoElement = document.getElementById('dbInfo');                setTimeout(() => this.sendMessage(), 500);        });



    addSourceInfo(results) {            

        if (results.length === 0) return;

                    if (data.status === 'healthy') {            };

        const sourceContent = results.map((result, index) => {

            const confidence = (result.similarity_score * 100).toFixed(0);                statusElement.className = 'status-indicator status-online';

            const source = result.metadata?.source || result.document_name;

            return `📄 ${source} <span class="confidence-score">%${confidence} güvenilir</span>`;                dbInfoElement.textContent = `${data.total_documents.toLocaleString()} ilaç prospektüsü hazır`;        const messageText = userInput.value.trim();

        }).join('<br>');

                    }

        const messagesContainer = document.getElementById('chatMessages');

        const sourceDiv = document.createElement('div');        } catch (error) {            this.recognition.onerror = (event) => {

        sourceDiv.className = 'assistant-message';

        sourceDiv.innerHTML = `            const statusElement = document.getElementById('status-indicator');

            <div class="message-avatar">

                <i class="fas fa-info-circle"></i>            const dbInfoElement = document.getElementById('dbInfo');                console.error('Ses tanıma hatası:', event.error);        // Hızlı arama butonları

            </div>

            <div class="message-content">            statusElement.className = 'status-indicator status-offline';

                <div class="source-info">

                    <strong>Kaynak Bilgileri:</strong><br>            dbInfoElement.textContent = 'Bağlantı hatası';            };

                    ${sourceContent}

                </div>        }

            </div>

        `;    }        document.addEventListener('click', (e) => {    setupEventListeners() {        if (messageText === '') return;

        

        messagesContainer.appendChild(sourceDiv);

        this.scrollToBottom();

    }    async sendMessage() {            this.recognition.onend = () => {



    showTypingIndicator(show) {        const input = document.getElementById('messageInput');

        const indicator = document.getElementById('typingIndicator');

        indicator.style.display = show ? 'flex' : 'none';        const message = input.value.trim();                this.isListening = false;            if (e.target.classList.contains('quick-search-btn')) {

        if (show) this.scrollToBottom();

    }        



    scrollToBottom() {        if (!message) return;                document.getElementById('voiceBtn').classList.remove('listening');

        const messagesContainer = document.getElementById('chatMessages');

        setTimeout(() => {

            messagesContainer.scrollTop = messagesContainer.scrollHeight;

        }, 100);        // Kullanıcı mesajını göster            };                document.getElementById('messageInput').value = e.target.textContent;        // Arama butonları

    }

}        this.addUserMessage(message);



// Uygulamayı başlat        input.value = '';        } else {

document.addEventListener('DOMContentLoaded', () => {

    new ProspektAsistan();

});
        // Yazıyor göstergesini göster            document.getElementById('voiceBtn').style.display = 'none';                this.sendMessage();

        this.showTypingIndicator(true);

        }

        try {

            // API'ye istek gönder    }            }        document.getElementById('searchBtn').addEventListener('click', () => this.performSearch());        appendMessage(messageText, 'user');

            const response = await this.searchDrug(message);

            await this.handleResponse(message, response);

        } catch (error) {

            this.addAssistantMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'error');    setupQuickSearches() {        });

        } finally {

            this.showTypingIndicator(false);        const quickSearches = [

        }

    }            'Aspirin yan etkileri',    }        document.getElementById('voiceBtn').addEventListener('click', () => this.toggleVoiceSearch());        userInput.value = '';



    async searchDrug(query) {            'Parol doz bilgisi',

        const response = await fetch(`${this.API_BASE}/search/vector`, {

            method: 'POST',            'Antibiyotik nasıl kullanılır',

            headers: {

                'Content-Type': 'application/json',            'Ağrı kesici önerileri',

            },

            body: JSON.stringify({            'Vitamin D faydaları',    setupVoiceRecognition() {        

                query: query,

                limit: 5,            'Hamilelik vitaminleri',

                minimum_similarity: 0.1,

                use_llm: true            'Soğuk algınlığı ilaçları',        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {

            })

        });            'Mide koruyucu ilaçlar'



        if (!response.ok) {        ];            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;        // Enter tuşu ile arama        fetch(apiUrl, {

            throw new Error(`API Hatası: ${response.status}`);

        }



        return await response.json();        const container = document.querySelector('.quick-searches');            this.recognition = new SpeechRecognition();

    }

        container.innerHTML = '';

    async handleResponse(userQuery, searchData) {

        if (!searchData.results || searchData.results.length === 0) {        quickSearches.forEach(search => {            this.recognition.lang = 'tr-TR';        document.getElementById('searchInput').addEventListener('keypress', (e) => {            method: 'POST',

            this.addAssistantMessage('Bu konu hakkında maalesef bilgi bulamadım. Başka bir ilaç veya soru deneyebilirsiniz.');

            return;            const btn = document.createElement('button');

        }

            btn.className = 'quick-search-btn';            this.recognition.continuous = false;

        // AI yanıtı varsa önce onu göster

        if (searchData.llm_response) {            btn.textContent = search;

            this.addAssistantMessage(searchData.llm_response.llm_answer, 'ai-response');

        }            container.appendChild(btn);            this.recognition.interimResults = false;            if (e.key === 'Enter') {            headers: {



        // Kaynak bilgileri göster        });

        this.addSourceInfo(searchData.results.slice(0, 3));

    }    }



    addUserMessage(content) {

        const messagesContainer = document.getElementById('chatMessages');

            toggleVoiceSearch() {            this.recognition.onstart = () => {                this.performSearch();                'Content-Type': 'application/json',

        const messageDiv = document.createElement('div');

        messageDiv.className = 'user-message';        if (!this.recognition) return;

        messageDiv.innerHTML = `

            <div class="message-avatar">                this.isListening = true;

                <i class="fas fa-user"></i>

            </div>        if (this.isListening) {

            <div class="message-content">

                ${content}            this.recognition.stop();                document.getElementById('voiceBtn').classList.add('listening');            }            },

            </div>

        `;        } else {

        

        messagesContainer.appendChild(messageDiv);            this.recognition.start();            };

        this.scrollToBottom();

    }        }



    addAssistantMessage(content, extraClass = '') {    }        });            body: JSON.stringify({ message: messageText }),

        const messagesContainer = document.getElementById('chatMessages');

        

        const messageDiv = document.createElement('div');

        messageDiv.className = `assistant-message ${extraClass}`;    async checkAPIStatus() {            this.recognition.onresult = (event) => {

        messageDiv.innerHTML = `

            <div class="message-avatar">        try {

                <i class="fas fa-user-md"></i>

            </div>            const response = await fetch(`${this.API_BASE}/health`);                const transcript = event.results[0][0].transcript;        })

            <div class="message-content">

                ${content}            const data = await response.json();

            </div>

        `;                            document.getElementById('messageInput').value = transcript;

        

        messagesContainer.appendChild(messageDiv);            const statusElement = document.getElementById('status-indicator');

        this.scrollToBottom();

    }            const dbInfoElement = document.getElementById('dbInfo');                setTimeout(() => this.sendMessage(), 500);        // Hızlı arama butonları        .then(response => response.json())



    addSourceInfo(results) {            

        if (results.length === 0) return;

                    if (data.status === 'healthy') {            };

        const sourceContent = results.map((result, index) => {

            const confidence = (result.similarity_score * 100).toFixed(0);                statusElement.className = 'status-indicator status-online';

            const source = result.metadata?.source || result.document_name;

            return `📄 ${source} <span class="confidence-score">%${confidence} güvenilir</span>`;                dbInfoElement.textContent = `${data.total_documents.toLocaleString()} ilaç prospektüsü hazır`;        document.addEventListener('click', (e) => {        .then(data => {

        }).join('<br>');

                    }

        const messagesContainer = document.getElementById('chatMessages');

        const sourceDiv = document.createElement('div');        } catch (error) {            this.recognition.onerror = (event) => {

        sourceDiv.className = 'assistant-message';

        sourceDiv.innerHTML = `            const statusElement = document.getElementById('status-indicator');

            <div class="message-avatar">

                <i class="fas fa-info-circle"></i>            const dbInfoElement = document.getElementById('dbInfo');                console.error('Ses tanıma hatası:', event.error);            if (e.target.classList.contains('quick-search-btn')) {            appendMessage(data.response, 'bot');

            </div>

            <div class="message-content">            statusElement.className = 'status-indicator status-offline';

                <div class="source-info">

                    <strong>Kaynak Bilgileri:</strong><br>            dbInfoElement.textContent = 'Bağlantı hatası';            };

                    ${sourceContent}

                </div>        }

            </div>

        `;    }                document.getElementById('searchInput').value = e.target.textContent;        })

        

        messagesContainer.appendChild(sourceDiv);

        this.scrollToBottom();

    }    async sendMessage() {            this.recognition.onend = () => {



    showTypingIndicator(show) {        const input = document.getElementById('messageInput');

        const indicator = document.getElementById('typingIndicator');

        indicator.style.display = show ? 'flex' : 'none';        const message = input.value.trim();                this.isListening = false;                this.performSearch();        .catch(error => {

        if (show) this.scrollToBottom();

    }        



    scrollToBottom() {        if (!message) return;                document.getElementById('voiceBtn').classList.remove('listening');

        const messagesContainer = document.getElementById('chatMessages');

        setTimeout(() => {

            messagesContainer.scrollTop = messagesContainer.scrollHeight;

        }, 100);        // Kullanıcı mesajını göster            };            }            console.error('API ile iletişim hatası:', error);

    }

}        this.addUserMessage(message);



// Uygulamayı başlat        input.value = '';        } else {

document.addEventListener('DOMContentLoaded', () => {

    new ProspektAsistan();

});
        // Yazıyor göstergesini göster            document.getElementById('voiceBtn').style.display = 'none';        });            appendMessage('Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin.', 'bot');

        this.showTypingIndicator(true);

        }

        try {

            // API'ye istek gönder    }    }        });

            const response = await this.searchDrug(message);

            await this.handleResponse(message, response);

        } catch (error) {

            this.addAssistantMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'error');    setupQuickSearches() {    }

        } finally {

            this.showTypingIndicator(false);        const quickSearches = [

        }

    }            'Aspirin yan etkileri',    setupVoiceRecognition() {



    async searchDrug(query) {            'Parol doz bilgisi',

        const response = await fetch(`${this.API_BASE}/search/vector`, {

            method: 'POST',            'Antibiyotik nasıl kullanılır',        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {    function appendMessage(text, sender) {

            headers: {

                'Content-Type': 'application/json',            'Ağrı kesici önerileri',

            },

            body: JSON.stringify({            'Vitamin D faydaları',            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;        const messageElement = document.createElement('div');

                query: query,

                limit: 5,            'Hamilelik vitaminleri',

                minimum_similarity: 0.1,

                use_llm: true            'Soğuk algınlığı ilaçları',            this.recognition = new SpeechRecognition();        messageElement.classList.add('message', `${sender}-message`);

            })

        });            'Mide koruyucu ilaçlar'



        if (!response.ok) {        ];            this.recognition.lang = 'tr-TR';        

            throw new Error(`API Hatası: ${response.status}`);

        }



        return await response.json();        const container = document.querySelector('.quick-searches');            this.recognition.continuous = false;        const p = document.createElement('p');

    }

        container.innerHTML = '';

    async handleResponse(userQuery, searchData) {

        if (!searchData.results || searchData.results.length === 0) {        quickSearches.forEach(search => {            this.recognition.interimResults = false;        p.textContent = text;

            this.addAssistantMessage('Bu konu hakkında maalesef bilgi bulamadım. Başka bir ilaç veya soru deneyebilirsiniz.');

            return;            const btn = document.createElement('button');

        }

            btn.className = 'quick-search-btn';        messageElement.appendChild(p);

        // AI yanıtı varsa önce onu göster

        if (searchData.llm_response) {            btn.textContent = search;

            this.addAssistantMessage(searchData.llm_response.llm_answer, 'ai-response');

        }            container.appendChild(btn);            this.recognition.onstart = () => {        



        // Kaynak bilgileri göster        });

        this.addSourceInfo(searchData.results.slice(0, 3));

    }    }                this.isListening = true;        chatBox.appendChild(messageElement);



    addUserMessage(content) {

        const messagesContainer = document.getElementById('chatMessages');

            toggleVoiceSearch() {                document.getElementById('voiceBtn').classList.add('listening');        chatBox.scrollTop = chatBox.scrollHeight;

        const messageDiv = document.createElement('div');

        messageDiv.className = 'user-message';        if (!this.recognition) return;

        messageDiv.innerHTML = `

            <div class="message-avatar">                this.showMessage('Dinliyorum... Konuşabilirsiniz.', 'info');    }

                <i class="fas fa-user"></i>

            </div>        if (this.isListening) {

            <div class="message-content">

                ${content}            this.recognition.stop();            };});

            </div>

        `;        } else {

        

        messagesContainer.appendChild(messageDiv);            this.recognition.start();

        this.scrollToBottom();

    }        }            this.recognition.onresult = (event) => {



    addAssistantMessage(content, extraClass = '') {    }                const transcript = event.results[0][0].transcript;

        const messagesContainer = document.getElementById('chatMessages');

                        document.getElementById('searchInput').value = transcript;

        const messageDiv = document.createElement('div');

        messageDiv.className = `assistant-message ${extraClass}`;    async checkAPIStatus() {                this.showMessage(`"${transcript}" algılandı`, 'success');

        messageDiv.innerHTML = `

            <div class="message-avatar">        try {                setTimeout(() => this.performSearch(), 1000);

                <i class="fas fa-user-md"></i>

            </div>            const response = await fetch(`${this.API_BASE}/health`);            };

            <div class="message-content">

                ${content}            const data = await response.json();

            </div>

        `;                        this.recognition.onerror = (event) => {

        

        messagesContainer.appendChild(messageDiv);            const statusElement = document.getElementById('status-indicator');                this.showMessage('Ses tanıma hatası: ' + event.error, 'error');

        this.scrollToBottom();

    }            const dbInfoElement = document.getElementById('dbInfo');            };



    addSourceInfo(results) {            

        if (results.length === 0) return;

                    if (data.status === 'healthy') {            this.recognition.onend = () => {

        const sourceContent = results.map((result, index) => {

            const confidence = (result.similarity_score * 100).toFixed(0);                statusElement.className = 'status-indicator status-online';                this.isListening = false;

            const source = result.metadata?.source || result.document_name;

            return `📄 ${source} <span class="confidence-score">%${confidence} güvenilir</span>`;                dbInfoElement.textContent = `${data.total_documents.toLocaleString()} ilaç prospektüsü hazır`;                document.getElementById('voiceBtn').classList.remove('listening');

        }).join('<br>');

                    }            };

        const messagesContainer = document.getElementById('chatMessages');

        const sourceDiv = document.createElement('div');        } catch (error) {        } else {

        sourceDiv.className = 'assistant-message';

        sourceDiv.innerHTML = `            const statusElement = document.getElementById('status-indicator');            document.getElementById('voiceBtn').style.display = 'none';

            <div class="message-avatar">

                <i class="fas fa-info-circle"></i>            const dbInfoElement = document.getElementById('dbInfo');        }

            </div>

            <div class="message-content">            statusElement.className = 'status-indicator status-offline';    }

                <div class="source-info">

                    <strong>Kaynak Bilgileri:</strong><br>            dbInfoElement.textContent = 'Bağlantı hatası';

                    ${sourceContent}

                </div>        }    setupQuickSearches() {

            </div>

        `;    }        const quickSearches = [

        

        messagesContainer.appendChild(sourceDiv);            'aspirin yan etkiler',

        this.scrollToBottom();

    }    async sendMessage() {            'parol doz',



    showTypingIndicator(show) {        const input = document.getElementById('messageInput');            'antibiyotik kullanım',

        const indicator = document.getElementById('typingIndicator');

        indicator.style.display = show ? 'flex' : 'none';        const message = input.value.trim();            'ağrı kesici',

        if (show) this.scrollToBottom();

    }                    'ateş düşürücü',



    scrollToBottom() {        if (!message) return;            'vitamin D',

        const messagesContainer = document.getElementById('chatMessages');

        setTimeout(() => {            'kalsiyum',

            messagesContainer.scrollTop = messagesContainer.scrollHeight;

        }, 100);        // Kullanıcı mesajını göster            'hamilelik vitamini'

    }

}        this.addUserMessage(message);        ];



// Uygulamayı başlat        input.value = '';

document.addEventListener('DOMContentLoaded', () => {

    new ProspektAsistan();        const container = document.querySelector('.quick-searches');

});
        // Yazıyor göstergesini göster        quickSearches.forEach(search => {

        this.showTypingIndicator(true);            const btn = document.createElement('button');

            btn.className = 'quick-search-btn';

        try {            btn.textContent = search;

            // API'ye istek gönder            container.appendChild(btn);

            const response = await this.searchDrug(message);        });

            await this.handleResponse(message, response);    }

        } catch (error) {

            this.addAssistantMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'error');    toggleVoiceSearch() {

        } finally {        if (!this.recognition) {

            this.showTypingIndicator(false);            this.showMessage('Ses tanıma bu tarayıcıda desteklenmiyor', 'error');

        }            return;

    }        }



    async searchDrug(query) {        if (this.isListening) {

        const response = await fetch(`${this.API_BASE}/search/vector`, {            this.recognition.stop();

            method: 'POST',        } else {

            headers: {            this.recognition.start();

                'Content-Type': 'application/json',        }

            },    }

            body: JSON.stringify({

                query: query,    async checkAPIStatus() {

                top_k: 5,        try {

                search_type: 'similarity',            const response = await fetch(`${this.API_BASE}/health`);

                include_metadata: true            const data = await response.json();

            })            

        });            const statusElement = document.getElementById('apiStatus');

            if (data.status === 'OK') {

        if (!response.ok) {                statusElement.innerHTML = '<span class="status-indicator status-online"></span>API Aktif';

            throw new Error(`API Hatası: ${response.status}`);                statusElement.className = 'api-status online';

        }                

                // Veritabanı bilgilerini göster

        return await response.json();                const dbInfo = await this.getDatabaseInfo();

    }                document.getElementById('dbInfo').textContent = 

                    `${dbInfo.document_count.toLocaleString()} döküman hazır`;

    async handleResponse(userQuery, searchData) {            }

        if (!searchData.results || searchData.results.length === 0) {        } catch (error) {

            this.addAssistantMessage('Bu konu hakkında maalesef bilgi bulamadım. Başka bir ilaç veya soru deneyebilirsiniz.');            const statusElement = document.getElementById('apiStatus');

            return;            statusElement.innerHTML = '<span class="status-indicator status-offline"></span>API Offline';

        }            statusElement.className = 'api-status offline';

            this.showMessage('API bağlantı hatası', 'error');

        // İlaç adını tespit et        }

        const drugName = this.extractDrugName(userQuery, searchData.results);    }

        

        if (drugName && drugName !== this.currentDrug) {    async getDatabaseInfo() {

            // Yeni ilaç - genel bilgi ver        try {

            this.currentDrug = drugName;            const response = await fetch(`${this.API_BASE}/database/info`);

            await this.provideDrugOverview(drugName, searchData.results);            return await response.json();

        } else {        } catch (error) {

            // Mevcut ilaç hakkında spesifik soru - detaylı cevap ver            return { document_count: 0 };

            await this.provideSpecificAnswer(userQuery, searchData.results);        }

        }    }

    }

    async performSearch() {

    extractDrugName(query, results) {        const query = document.getElementById('searchInput').value.trim();

        // İlk sonuçtan ilaç adını çıkarmaya çalış        if (!query) {

        if (results.length > 0 && results[0].metadata?.drug_name) {            this.showMessage('Lütfen arama terimi girin', 'error');

            return results[0].metadata.drug_name;            return;

        }        }

        

        // Query'den potansiyel ilaç adını çıkar        this.showLoading(true);

        const commonDrugs = ['aspirin', 'parol', 'ibuprofen', 'parasetamol', 'augmentin', 'omeprazol', 'vitamin'];        this.hideResults();

        for (let drug of commonDrugs) {

            if (query.toLowerCase().includes(drug)) {        try {

                return drug.charAt(0).toUpperCase() + drug.slice(1);            const searchParams = this.getSearchParams(query);

            }            const response = await fetch(`${this.API_BASE}/search/vector`, {

        }                method: 'POST',

                        headers: {

        return null;                    'Content-Type': 'application/json',

    }                },

                body: JSON.stringify(searchParams)

    async provideDrugOverview(drugName, results) {            });

        // Genel ilaç bilgisi

        const overviewContent = this.generateDrugOverview(drugName, results);            if (!response.ok) {

        this.addAssistantMessage(overviewContent, 'drug-info');                throw new Error(`HTTP ${response.status}: ${response.statusText}`);

                    }

        // Kaynak bilgileri

        this.addSourceInfo(results.slice(0, 3));            const data = await response.json();

    }            this.displayResults(data, query);



    async provideSpecificAnswer(query, results) {        } catch (error) {

        // Kullanıcının spesifik sorusuna cevap            this.showMessage(`Arama hatası: ${error.message}`, 'error');

        const specificContent = this.generateSpecificAnswer(query, results);        } finally {

        this.addAssistantMessage(specificContent);            this.showLoading(false);

                }

        // En alakalı kaynağı göster    }

        if (results.length > 0) {

            this.addSourceInfo([results[0]]);    getSearchParams(query) {

        }        return {

    }            query: query,

            top_k: parseInt(document.getElementById('topK').value) || 5,

    generateDrugOverview(drugName, results) {            search_type: document.getElementById('searchType').value || 'similarity',

        const topResult = results[0];            include_metadata: document.getElementById('includeMetadata').checked

        const content = topResult.content || topResult.text || '';        };

            }

        return `

            <h4><i class="fas fa-pills"></i> ${drugName} Hakkında Genel Bilgi</h4>    displayResults(data, query) {

            <p><strong>Temel Bilgiler:</strong></p>        const resultsSection = document.getElementById('resultsSection');

            <p>${this.extractKeyInfo(content, 'genel')}</p>        const resultsContainer = document.getElementById('resultsContainer');

                    

            <p><strong>Kullanım Alanları:</strong></p>        // Başlık güncelle

            <p>${this.extractKeyInfo(content, 'kullanim')}</p>        document.getElementById('searchQuery').textContent = query;

                    document.getElementById('resultCount').textContent = data.results?.length || 0;

            <p>Bu ilaç hakkında daha spesifik sorularınızı sorabilirsiniz. Örneğin: "yan etkileri neler?", "dozu nasıl?", "kimler kullanmamalı?" gibi...</p>        document.getElementById('searchTime').textContent = `${data.search_time_ms}ms`;

        `;

    }        // Sonuçları temizle

        resultsContainer.innerHTML = '';

    generateSpecificAnswer(query, results) {

        const relevantResult = results[0];        if (!data.results || data.results.length === 0) {

        const content = relevantResult.content || relevantResult.text || '';            resultsContainer.innerHTML = '<div class="no-results">Sonuç bulunamadı</div>';

                    resultsSection.style.display = 'block';

        if (query.toLowerCase().includes('yan etki')) {            return;

            return `<p><strong>Yan Etkiler:</strong></p><p>${this.extractKeyInfo(content, 'yan etki')}</p>`;        }

        } else if (query.toLowerCase().includes('doz')) {

            return `<p><strong>Doz Bilgisi:</strong></p><p>${this.extractKeyInfo(content, 'doz')}</p>`;        // LLM yanıtı varsa göster

        } else if (query.toLowerCase().includes('kullan')) {        if (data.llm_response) {

            return `<p><strong>Kullanım Şekli:</strong></p><p>${this.extractKeyInfo(content, 'kullanim')}</p>`;            this.displayLLMResponse(data.llm_response, resultsContainer);

        } else {        }

            return `<p>${content.substring(0, 300)}${content.length > 300 ? '...' : ''}</p>`;

        }        // Sonuçları göster

    }        data.results.forEach((result, index) => {

            const resultElement = this.createResultElement(result, index + 1);

    extractKeyInfo(content, type) {            resultsContainer.appendChild(resultElement);

        // Basit anahtar kelime tabanlı bilgi çıkarma        });

        const sentences = content.split(/[.!?]+/);

        const keywords = {        resultsSection.style.display = 'block';

            'yan etki': ['yan etki', 'istenmeyen', 'etki', 'reaksiyon'],        resultsSection.scrollIntoView({ behavior: 'smooth' });

            'doz': ['doz', 'miktar', 'günde', 'tablet', 'mg'],    }

            'kullanim': ['kullan', 'alın', 'kullanım', 'nasıl'],

            'genel': ['etken madde', 'içerik', 'nedir', 'tedavi']    createResultElement(result, index) {

        };        const div = document.createElement('div');

                div.className = 'result-item';

        const relevantSentences = sentences.filter(sentence => {        

            return keywords[type]?.some(keyword =>         const score = (result.score * 100).toFixed(1);

                sentence.toLowerCase().includes(keyword.toLowerCase())        const title = result.metadata?.title || result.metadata?.source || `Sonuç ${index}`;

            );        const text = result.content || result.text || 'İçerik bulunamadı';

        });        

                div.innerHTML = `

        return relevantSentences.slice(0, 2).join('. ') ||             <div class="result-title">

               content.substring(0, 150) + '...';                <i class="fas fa-pills"></i> ${title}

    }            </div>

            <div class="result-score">Benzerlik: %${score}</div>

    addUserMessage(content) {            <div class="result-text">${this.highlightText(text)}</div>

        const messagesContainer = document.getElementById('chatMessages');            ${this.renderMetadata(result.metadata)}

                `;

        const messageDiv = document.createElement('div');

        messageDiv.className = 'user-message';        return div;

        messageDiv.innerHTML = `    }

            <div class="message-avatar">

                <i class="fas fa-user"></i>    renderMetadata(metadata) {

            </div>        if (!metadata) return '';

            <div class="message-content">        

                ${content}        const items = [];

            </div>        if (metadata.source) items.push(`📄 ${metadata.source}`);

        `;        if (metadata.page) items.push(`📃 Sayfa ${metadata.page}`);

                if (metadata.drug_name) items.push(`💊 ${metadata.drug_name}`);

        messagesContainer.appendChild(messageDiv);        

        this.scrollToBottom();        return items.length > 0 ? 

    }            `<div class="result-metadata">${items.join(' • ')}</div>` : '';

    }

    addAssistantMessage(content, extraClass = '') {

        const messagesContainer = document.getElementById('chatMessages');    displayLLMResponse(response, container) {

                const div = document.createElement('div');

        const messageDiv = document.createElement('div');        div.className = 'llm-answer';

        messageDiv.className = `assistant-message ${extraClass}`;        div.innerHTML = `

        messageDiv.innerHTML = `            <h3>

            <div class="message-avatar">                <i class="fas fa-robot"></i> AI Asistan Yanıtı

                <i class="fas fa-user-md"></i>            </h3>

            </div>            <div>${response}</div>

            <div class="message-content">        `;

                ${content}        container.appendChild(div);

            </div>    }

        `;

            highlightText(text, maxLength = 300) {

        messagesContainer.appendChild(messageDiv);        const truncated = text.length > maxLength ? 

        this.scrollToBottom();            text.substring(0, maxLength) + '...' : text;

    }        

        // Arama terimini vurgula

    addSourceInfo(results) {        const query = document.getElementById('searchInput').value.trim();

        if (results.length === 0) return;        if (query) {

                    const regex = new RegExp(`(${query})`, 'gi');

        const sourceContent = results.map((result, index) => {            return truncated.replace(regex, '<mark>$1</mark>');

            const confidence = (result.score * 100).toFixed(0);        }

            const source = result.metadata?.source || 'Bilinmeyen kaynak';        return truncated;

            return `📄 ${source} <span class="confidence-score">%${confidence} güvenilir</span>`;    }

        }).join('<br>');

            showLoading(show) {

        const messagesContainer = document.getElementById('chatMessages');        document.getElementById('loading').style.display = show ? 'block' : 'none';

        const sourceDiv = document.createElement('div');    }

        sourceDiv.className = 'assistant-message';

        sourceDiv.innerHTML = `    hideResults() {

            <div class="message-avatar">        document.getElementById('resultsSection').style.display = 'none';

                <i class="fas fa-info-circle"></i>    }

            </div>

            <div class="message-content">    showMessage(message, type = 'info') {

                <div class="source-info">        // Mevcut mesajları temizle

                    <strong>Kaynak Bilgileri:</strong><br>        const existingMessages = document.querySelectorAll('.message');

                    ${sourceContent}        existingMessages.forEach(msg => msg.remove());

                </div>

            </div>        const div = document.createElement('div');

        `;        div.className = `message ${type}`;

                div.textContent = message;

        messagesContainer.appendChild(sourceDiv);        

        this.scrollToBottom();        const container = document.querySelector('.search-section');

    }        container.appendChild(div);



    showTypingIndicator(show) {        // 5 saniye sonra mesajı kaldır

        const indicator = document.getElementById('typingIndicator');        setTimeout(() => div.remove(), 5000);

        indicator.style.display = show ? 'flex' : 'none';    }

        if (show) this.scrollToBottom();}

    }

// Uygulamayı başlat

    scrollToBottom() {document.addEventListener('DOMContentLoaded', () => {

        const messagesContainer = document.getElementById('chatMessages');    new PupillicaApp();

        setTimeout(() => {});

            messagesContainer.scrollTop = messagesContainer.scrollHeight;

        }, 100);// Genel CSS sınıfları

    }const style = document.createElement('style');

}style.textContent = `

    .message {

// Uygulamayı başlat        padding: 10px 15px;

document.addEventListener('DOMContentLoaded', () => {        margin: 10px 0;

    new ProspektAsistan();        border-radius: 8px;

});        font-weight: 500;
    }
    
    .message.info {
        background: #e3f2fd;
        color: #1976d2;
        border-left: 4px solid #2196f3;
    }
    
    .message.success {
        background: #e8f5e8;
        color: #2e7d32;
        border-left: 4px solid #4caf50;
    }
    
    .message.error {
        background: #ffebee;
        color: #c62828;
        border-left: 4px solid #f44336;
    }
    
    .api-status {
        font-size: 0.9rem;
        padding: 5px 10px;
        border-radius: 15px;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .api-status.online {
        background: #e8f5e8;
        color: #2e7d32;
    }
    
    .api-status.offline {
        background: #ffebee;
        color: #c62828;
    }
    
    .no-results {
        text-align: center;
        padding: 40px;
        color: #666;
        font-size: 1.2rem;
    }
    
    mark {
        background: #fff3cd;
        padding: 2px 4px;
        border-radius: 3px;
    }
`;
document.head.appendChild(style);