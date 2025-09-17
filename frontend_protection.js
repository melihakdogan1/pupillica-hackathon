"""
Rate limiting ve güvenlik önlemleri
Frontend'e eklenecek koruma kodu
"""

// Rate limiting for frontend
class RateLimiter {
    constructor(maxRequests = 10, timeWindow = 60000) { // 10 requests per minute
        this.maxRequests = maxRequests;
        this.timeWindow = timeWindow;
        this.requests = [];
    }
    
    canMakeRequest() {
        const now = Date.now();
        // Remove old requests
        this.requests = this.requests.filter(time => now - time < this.timeWindow);
        
        if (this.requests.length >= this.maxRequests) {
            return false;
        }
        
        this.requests.push(now);
        return true;
    }
    
    getRemainingTime() {
        if (this.requests.length === 0) return 0;
        const oldestRequest = Math.min(...this.requests);
        return Math.max(0, this.timeWindow - (Date.now() - oldestRequest));
    }
}

// Usage in search function
const rateLimiter = new RateLimiter(10, 60000); // 10 searches per minute

async function performSearchWithLimiting(query) {
    if (!rateLimiter.canMakeRequest()) {
        const waitTime = Math.ceil(rateLimiter.getRemainingTime() / 1000);
        alert(`Çok fazla arama yaptınız. ${waitTime} saniye bekleyin.`);
        return;
    }
    
    // Normal search continues...
    return await searchPupillica(query);
}