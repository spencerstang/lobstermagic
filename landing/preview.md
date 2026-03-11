# BotBridge Landing Page Preview

## Visual Layout:

### Header (White, Sticky)
- Logo: "🤖 BotBridge" 
- Nav: Features | Pricing | Retailers | API Docs | [Get API Key]

### Hero Section (Purple-Blue Gradient)
- **H1:** "Your Bridge to Retail Data"
- **Subtitle:** "Stop fighting bot detection. Start building."
- **Buttons:** [Start Free Trial] [View Documentation]

### Features Section (3 Cards)
1. **⚡ It Just Works**
   - No more 403 errors, CAPTCHAs, or IP bans
   
2. **🔄 Real-Time Data**
   - Current prices, stock levels, product details
   
3. **🛠️ Developer First**
   - Clean REST API, great docs, responsive support

### Code Sample (Dark Terminal Style)
```javascript
const response = await fetch('https://api.botbridge.ai/v1/search', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your_api_key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'milwaukee impact driver',
    retailers: ['lowes', 'homedepot'],
    zip_code: '10001'
  })
});
```

### Pricing Section (3 Tiers)
- **Hobbyist:** $10/mo (₿ $9 with Bitcoin)
- **Startup:** $49/mo (₿ $44 with Bitcoin) - "Most Popular" badge
- **Growth:** $199/mo (₿ $179 with Bitcoin)

### Retailers Grid
- **Lowe's:** ✅ Live Now
- **Home Depot:** Coming March 18
- **Menards:** Coming March 18
- **Target:** Coming April 2026
- **Walmart:** Coming April 2026
- **Best Buy:** Coming Soon

### Footer (Dark)
- Links: API Docs | Terms | Privacy | Status | Support
- "Built with ❤️ for the bot economy"

## Design Details:
- Modern, clean, developer-focused
- Purple/blue gradient accents (#667eea to #764ba2)
- Card-based layout with hover effects
- Mobile responsive
- Professional typography