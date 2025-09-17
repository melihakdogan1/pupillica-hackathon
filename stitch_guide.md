# 🎨 PUPILLICA GOOGLE STITCH DESIGN GUIDE

## 🚀 Quick Setup Steps

### 1. Create Stitch Project
- Go to: https://stitch.withgoogle.com
- New Project: "Pupillica Drug Search"
- Select: "Web App" template

### 2. Required Components

#### 📝 Header Section
```
Component: Header Bar
- Title: "🏥 Pupillica"
- Subtitle: "Türkiye İlaç Bilgi Sistemi"
- Background: Material Blue (Primary)
```

#### 🔍 Search Section  
```
Component: Search Bar
- Input: Text field (full width)
- Placeholder: "İlaç adı, yan etki, doz bilgisi yazın..."
- Button: "🔍 Ara" (Material Button, Primary)
- Style: Material Design outlined
```

#### 📋 Quick Examples
```
Component: Chip Group
Chips: [
  "paracetamol yan etki",
  "aspirin doz", 
  "antibiyotik",
  "ağrı kesici",
  "ateş düşürücü"
]
- Style: Material Chips, clickable
```

#### 📊 Status Display
```
Component: Text Display
- Shows: API status, search results count
- Style: Caption text, centered
```

#### 📄 Results List
```
Component: Card List
Each Card:
- Title: Document name
- Subtitle: Document type + similarity %
- Body: Text snippet (3 lines max)
- Style: Material Cards with elevation
```

### 3. JavaScript Integration

Copy `stitch_integration.js` content to Stitch:

```javascript
// 1. Add this to Stitch JavaScript section
[stitch_integration.js content]

// 2. Wire up events:
searchButton.onClick = async () => {
    const results = await searchPupillica(searchInput.value);
    displayResults(results);
};

// 3. Initialize on load:
window.onload = () => {
    initializePupillica();
};
```

### 4. Color Scheme
```
Primary: #667eea (Material Blue)
Secondary: #ff6b6b (Material Red)
Surface: #ffffff
Background: #f5f5f5
Text: #212121
```

### 5. Responsive Breakpoints
```
Mobile: < 600px (single column)
Tablet: 600px - 1024px (2 columns)
Desktop: > 1024px (3 columns)
```

## 🎯 Implementation Timeline

### Hour 1: Basic Setup
- [ ] Create Stitch project
- [ ] Add header and search components
- [ ] Basic layout design

### Hour 2: API Integration  
- [ ] Copy JavaScript code
- [ ] Wire up search functionality
- [ ] Test basic search

### Hour 3: Polish & Test
- [ ] Add loading states
- [ ] Improve error handling
- [ ] Mobile responsiveness check

## 📱 Mobile-First Design

### Priority Order:
1. Search input (most important)
2. Quick example chips
3. Results list
4. Status/stats (least important on mobile)

### Touch Targets:
- Minimum 44px touch targets
- Easy thumb navigation
- Large search button

## 🔧 Testing Checklist

### Functionality:
- [ ] Search works with API
- [ ] Example chips clickable
- [ ] Results display correctly
- [ ] Error messages show
- [ ] Loading states work

### Performance:
- [ ] < 3 second page load
- [ ] Smooth animations
- [ ] Responsive on all devices

### Accessibility:
- [ ] Keyboard navigation
- [ ] Screen reader friendly
- [ ] High contrast support

## 🚀 Deployment

Stitch provides automatic hosting:
- URL: `https://[project-name].stitch.withgoogle.com`
- Custom domain possible
- SSL included
- Global CDN

## 📞 API Endpoints Reference

```javascript
// Health Check
GET http://localhost:8000/health

// Search  
GET http://localhost:8000/search?q=QUERY&limit=10

// Response format:
{
  "success": true,
  "results": [...],
  "total_results": 5,
  "search_time_ms": 250
}
```

Start with Stitch now! 🎨