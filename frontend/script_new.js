class ProspektAsistan {
    constructor() {
        // GitHub Pages demo için API URL
        this.API_BASE = window.location.hostname === 'melihakdogan1.github.io' 
            ? 'https://prospektasistan-api.herokuapp.com' // Heroku backup
            : 'http://127.0.0.1:8003'; // Local development
        
        this.isListening = false;
        this.recognition = null;
        this.currentDrug = null;
        this.conversationHistory = [];
        this.isDemoMode = window.location.hostname === 'melihakdogan1.github.io';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAPIStatus();
        this.setupVoiceRecognition();
        this.setupQuickSearches();
    }

    setupEventListeners() {
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('voiceBtn').addEventListener('click', () => this.toggleVoiceSearch());
        
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-search-btn')) {
                document.getElementById('messageInput').value = e.target.textContent;
                this.sendMessage();
            }
        });
    }

    setupVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'tr-TR';
            this.recognition.continuous = false;
            this.recognition.interimResults = false;

            this.recognition.onstart = () => {
                this.isListening = true;
                document.getElementById('voiceBtn').classList.add('listening');
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('messageInput').value = transcript;
                setTimeout(() => this.sendMessage(), 500);
            };

            this.recognition.onerror = (event) => {
                console.error('Ses tanıma hatası:', event.error);
            };

            this.recognition.onend = () => {
                this.isListening = false;
                document.getElementById('voiceBtn').classList.remove('listening');
            };
        } else {
            document.getElementById('voiceBtn').style.display = 'none';
        }
    }

    setupQuickSearches() {
        const quickSearches = [
            'Aspirin yan etkileri',
            'Parol doz bilgisi',
            'Antibiyotik nasıl kullanılır',
            'Ağrı kesici önerileri',
            'Vitamin D faydaları',
            'Hamilelik vitaminleri',
            'Soğuk algınlığı ilaçları',
            'Mide koruyucu ilaçlar'
        ];

        const container = document.querySelector('.quick-searches');
        container.innerHTML = '';
        quickSearches.forEach(search => {
            const btn = document.createElement('button');
            btn.className = 'quick-search-btn';
            btn.textContent = search;
            container.appendChild(btn);
        });
    }

    toggleVoiceSearch() {
        if (!this.recognition) return;

        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }

    async checkAPIStatus() {
        try {
            const statusElement = document.getElementById('status-indicator');
            const dbInfoElement = document.getElementById('dbInfo');
            
            if (this.isDemoMode) {
                // Demo mode status
                statusElement.className = 'status-indicator status-online';
                dbInfoElement.textContent = '6,425 demo ilaç prospektüsü (Demo Mode)';
                return;
            }
            
            const response = await fetch(`${this.API_BASE}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                statusElement.className = 'status-indicator status-online';
                dbInfoElement.textContent = `${data.total_documents.toLocaleString()} ilaç prospektüsü hazır`;
            }
        } catch (error) {
            const statusElement = document.getElementById('status-indicator');
            const dbInfoElement = document.getElementById('dbInfo');
            statusElement.className = 'status-indicator status-offline';
            dbInfoElement.textContent = this.isDemoMode ? 'Demo Mode - Çevrimdışı' : 'Bağlantı hatası';
        }
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message) return;

        this.addUserMessage(message);
        input.value = '';
        this.showTypingIndicator(true);

        try {
            const response = await this.searchDrug(message);
            await this.handleResponse(message, response);
        } catch (error) {
            this.addAssistantMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'error');
        } finally {
            this.showTypingIndicator(false);
        }
    }

    async searchDrug(query) {
        if (this.isDemoMode) {
            return await this.getMockResponse(query);
        }

        const response = await fetch(`${this.API_BASE}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                limit: 5,
                minimum_similarity: 0.1,
                use_llm: true
            })
        });

        if (!response.ok) {
            throw new Error(`API Hatası: ${response.status}`);
        }

        return await response.json();
    }

    async getMockResponse(query) {
        // Demo için gecikme simülasyonu
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
        
        const queryLower = query.toLowerCase();
        
        // Aspirin sorguları için mock yanıt
        if (queryLower.includes('aspirin')) {
            return {
                results: [
                    {
                        metadata: {
                            source: "aspirin_prospektus.pdf",
                            drug_name: "Aspirin"
                        },
                        page_content: "Aspirin (Asetilsalisilik asit) ağrı kesici, ateş düşürücü ve anti-inflamatuar özelliklere sahiptir."
                    }
                ],
                llm_response: {
                    llm_answer: "🔍 **Aspirin** hakkında bilgiler bulundu:\n\n**Etken Madde:** Asetilsalisilik asit\n\n**Kullanım Alanları:**\n• Ağrı kesici (baş ağrısı, diş ağrısı)\n• Ateş düşürücü\n• Kalp krizi önleme (düşük doz)\n\n**Yan Etkiler:**\n• Mide rahatsızlığı\n• Kulak çınlaması (yüksek doz)\n• Kanama riski artışı\n\n**⚠️ Dikkat:** Çocuklarda Reye sendromu riski nedeniyle kullanılmamalıdır."
                }
            };
        }
        
        // Parol sorguları için mock yanıt
        if (queryLower.includes('parol') || queryLower.includes('parasetamol')) {
            return {
                results: [
                    {
                        metadata: {
                            source: "parol_prospektus.pdf",
                            drug_name: "Parol"
                        },
                        page_content: "Parol parasetamol içeren ağrı kesici ve ateş düşürücü ilaçtır."
                    }
                ],
                llm_response: {
                    llm_answer: "🔍 **Parol** hakkında bilgiler bulundu:\n\n**Etken Madde:** Parasetamol\n\n**Kullanım Alanları:**\n• Ağrı kesici\n• Ateş düşürücü\n• Baş ağrısı, kas ağrısı\n\n**Dozaj:**\n• Yetişkin: 500-1000 mg, günde 4 kez\n• Maksimum günlük doz: 4000 mg\n\n**Yan Etkiler:**\n• Nadiren karaciğer hasarı\n• Aşırı dozda toksik\n\n**✅ Güvenlik:** Gebelik ve emzirmede güvenli kabul edilir."
                }
            };
        }
        
        // Genel ağrı sorguları
        if (queryLower.includes('ağrı') || queryLower.includes('agri')) {
            return {
                results: [
                    {
                        metadata: {
                            source: "agri_kesiciler.pdf",
                            drug_name: "Ağrı Kesiciler"
                        },
                        page_content: "Ağrı kesici ilaçlar farklı etki mekanizmalarına sahiptir."
                    }
                ],
                llm_response: {
                    llm_answer: "🔍 **Ağrı Kesici İlaçlar** hakkında bilgi:\n\n**Sık Kullanılan Ağrı Kesiciler:**\n• **Parasetamol** (Parol, Tylol)\n• **Aspirin** (Asetilsalisilik asit)\n• **İbuprofen** (Majezik, Advil)\n• **Diklofenak** (Voltaren)\n\n**Seçim Kriterleri:**\n• Ağrının türü ve şiddeti\n• Kişinin yaşı ve sağlık durumu\n• Diğer ilaç kullanımı\n\n**💡 Hangi ilacın prospektüsünü incelemek istiyorsunuz?**"
                }
            };
        }
        
        // Default yanıt
        return {
            results: [
                {
                    metadata: {
                        source: "demo_bilgi.pdf",
                        drug_name: "Demo"
                    },
                    page_content: `"${query}" hakkında demo bilgisi.`
                }
            ],
            llm_response: {
                llm_answer: `🔍 **"${query}"** hakkında arama yapıldı.\n\n**Demo Mode Aktif** - Bu ProspektAsistan'ın demo versiyonudur.\n\n**Önerilen Aramalar:**\n• Aspirin\n• Parol\n• Ağrı kesici ilaçlar\n• Ateş düşürücü\n\n**💡 İpucu:** Daha spesifik ilaç adları veya belirtiler yazarsanız detaylı bilgi alabilirsiniz.\n\n**Tam Sürüm:** Gerçek ProspektAsistan 6,425+ ilaç prospektüsüne erişim sağlar.`
            }
        };
    }

    async handleResponse(userQuery, searchData) {
        if (!searchData.results || searchData.results.length === 0) {
            this.addAssistantMessage('Bu konu hakkında maalesef bilgi bulamadım. Başka bir ilaç veya soru deneyebilirsiniz.');
            return;
        }

        if (searchData.llm_response) {
            this.addAssistantMessage(searchData.llm_response.llm_answer, 'ai-response');
        }

        this.addSourceInfo(searchData.results.slice(0, 3));
    }

    addUserMessage(content) {
        const messagesContainer = document.getElementById('chatMessages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'user-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">
                ${content}
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addAssistantMessage(content, extraClass = '') {
        const messagesContainer = document.getElementById('chatMessages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `assistant-message ${extraClass}`;
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user-md"></i>
            </div>
            <div class="message-content">
                ${content}
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSourceInfo(results) {
        if (results.length === 0) return;
        
        const sourceContent = results.map((result, index) => {
            const confidence = (result.similarity_score * 100).toFixed(0);
            const source = result.metadata?.source || result.document_name;
            return `📄 ${source} <span class="confidence-score">%${confidence} güvenilir</span>`;
        }).join('<br>');
        
        const messagesContainer = document.getElementById('chatMessages');
        const sourceDiv = document.createElement('div');
        sourceDiv.className = 'assistant-message';
        sourceDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-info-circle"></i>
            </div>
            <div class="message-content">
                <div class="source-info">
                    <strong>Kaynak Bilgileri:</strong><br>
                    ${sourceContent}
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(sourceDiv);
        this.scrollToBottom();
    }

    showTypingIndicator(show) {
        const indicator = document.getElementById('typingIndicator');
        indicator.style.display = show ? 'flex' : 'none';
        if (show) this.scrollToBottom();
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ProspektAsistan();
});
