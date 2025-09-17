/**
 * 🏥 PUPILLICA API INTEGRATION FOR GOOGLE STITCH
 * Copy-paste ready JavaScript kod for Stitch project
 */

// API Configuration
const PUPILLICA_API = {
    baseUrl: 'http://localhost:8000',
    endpoints: {
        health: '/health',
        search: '/search',
        stats: '/stats'
    }
};

// API Health Check Function
async function checkPupillicaAPI() {
    try {
        const response = await fetch(`${PUPILLICA_API.baseUrl}${PUPILLICA_API.endpoints.health}`);
        const data = await response.json();
        
        return {
            success: true,
            status: data.status,
            totalDocuments: data.total_documents,
            message: `✅ ${data.total_documents.toLocaleString('tr-TR')} doküman hazır`
        };
    } catch (error) {
        return {
            success: false,
            message: '❌ API bağlantısı yok'
        };
    }
}

// Search Function
async function searchPupillica(query, limit = 10) {
    if (!query || query.trim().length === 0) {
        return {
            success: false,
            message: 'Lütfen arama terimi girin'
        };
    }

    try {
        const searchParams = new URLSearchParams({
            q: query.trim(),
            limit: limit,
            min_similarity: 0.2
        });
        
        const response = await fetch(
            `${PUPILLICA_API.baseUrl}${PUPILLICA_API.endpoints.search}?${searchParams}`
        );
        
        const data = await response.json();
        
        if (data.success && data.results.length > 0) {
            return {
                success: true,
                query: data.query,
                totalResults: data.total_results,
                searchTime: data.search_time_ms,
                results: data.results.map(result => ({
                    id: result.document_id,
                    title: result.document_name,
                    type: result.document_type,
                    text: result.text_chunk,
                    similarity: Math.round(result.similarity_score * 100),
                    highlighted: highlightSearchTerms(result.text_chunk, query)
                }))
            };
        } else {
            return {
                success: false,
                message: `"${query}" için sonuç bulunamadı`
            };
        }
        
    } catch (error) {
        console.error('Search error:', error);
        return {
            success: false,
            message: 'Arama sırasında hata oluştu'
        };
    }
}

// Highlight search terms in text
function highlightSearchTerms(text, query) {
    if (!query) return text;
    
    const terms = query.toLowerCase().split(' ').filter(term => term.length > 2);
    let highlightedText = text;
    
    terms.forEach(term => {
        const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
        highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
    });
    
    return highlightedText;
}

// Escape special regex characters
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Sample queries for quick testing
const SAMPLE_QUERIES = [
    'paracetamol yan etki',
    'aspirin doz', 
    'antibiyotik kullanım',
    'ağrı kesici',
    'ateş düşürücü',
    'hamilelik ilaç',
    'kan sulandırıcı',
    'mide koruyucu'
];

// Initialize function for Stitch
async function initializePupillica() {
    console.log('🏥 Pupillica API initializing...');
    
    const healthCheck = await checkPupillicaAPI();
    
    if (healthCheck.success) {
        console.log('✅ API connected:', healthCheck.message);
        return true;
    } else {
        console.log('❌ API connection failed:', healthCheck.message);
        return false;
    }
}

// Export for Stitch usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        checkPupillicaAPI,
        searchPupillica,
        highlightSearchTerms,
        SAMPLE_QUERIES,
        initializePupillica
    };
}

/**
 * 📋 GOOGLE STITCH IMPLEMENTATION GUIDE:
 * 
 * 1. Create new Stitch project
 * 2. Add search input component
 * 3. Add results display component  
 * 4. Copy this JavaScript code to Stitch
 * 5. Connect UI events to functions:
 *    - onSearch: call searchPupillica()
 *    - onInit: call initializePupillica()
 * 
 * Example Stitch usage:
 * ```javascript
 * // In Stitch event handler
 * const results = await searchPupillica(searchInput.value);
 * if (results.success) {
 *     displayResults(results.results);
 * } else {
 *     showError(results.message);
 * }
 * ```
 */