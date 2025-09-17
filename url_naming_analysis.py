"""
🏷️ URL İSİMLENDİRME STRATEJİSİ ANALİZİ
Hangi isim daha iyi: pupillica vs prospektusasistan?
"""

print("🏷️ URL İSİMLENDİRME KARŞILAŞTIRMASI")
print("=" * 50)

url_options = {
    "pupillica": {
        "domain": "pupillica.vercel.app",
        "anlam": "Pupil (göz bebeği) + Medical",
        "avantajlar": [
            "✅ Kısa ve akılda kalıcı",
            "✅ Medical vibe",
            "✅ Global appeal",
            "✅ Modern/tech sounds",
            "✅ Brand potential yüksek"
        ],
        "dezavantajlar": [
            "⚠️ Anlam net değil",
            "⚠️ Türkçe değil"
        ],
        "score": "8/10"
    },
    
    "prospektusasistan": {
        "domain": "prospektusasistan.vercel.app",
        "anlam": "Prospektüs + Asistan (çok net)",
        "avantajlar": [
            "✅ Çok net anlam",
            "✅ Türkçe",
            "✅ SEO friendly",
            "✅ Target audience net",
            "✅ Functional naming"
        ],
        "dezavantajlar": [
            "⚠️ Uzun URL",
            "⚠️ Typing zor",
            "⚠️ Brand potential düşük"
        ],
        "score": "7/10"
    },
    
    "ilacasistan": {
        "domain": "ilacasistan.vercel.app", 
        "anlam": "İlaç + Asistan",
        "avantajlar": [
            "✅ Çok net anlam",
            "✅ Kısa",
            "✅ Türkçe",
            "✅ SEO perfect",
            "✅ Hatırlanması kolay"
        ],
        "dezavantajlar": [
            "⚠️ Çok literal"
        ],
        "score": "9/10"
    }
}

for name, details in url_options.items():
    print(f"\n📋 {name.upper()}:")
    print(f"   🌐 URL: {details['domain']}")
    print(f"   💡 Anlam: {details['anlam']}")
    print(f"   📊 Score: {details['score']}")
    
    print(f"   ✅ Avantajlar:")
    for avantaj in details['avantajlar']:
        print(f"      {avantaj}")
    
    print(f"   ⚠️ Dezavantajlar:")
    for dezavantaj in details['dezavantajlar']:
        print(f"      {dezavantaj}")

print(f"\n🎯 ÖNERİ SIRALAMASI:")
print("1. 🥇 ilacasistan.vercel.app (9/10)")
print("2. 🥈 pupillica.vercel.app (8/10)")
print("3. 🥉 prospektusasistan.vercel.app (7/10)")

print(f"\n💡 EKSTRA FİKİRLER:")
extra_ideas = [
    "medicalsearch.vercel.app",
    "druginfo.vercel.app", 
    "titckasistan.vercel.app",
    "eczanebot.vercel.app",
    "ilacbul.vercel.app"
]

for idea in extra_ideas:
    print(f"   • {idea}")

print(f"\n🚀 HIZLI KARAR: ilacasistan kullan!")
print("En net, en SEO-friendly, en akılda kalıcı!")