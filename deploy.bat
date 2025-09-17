@echo off
echo 🚀 İlaç Asistanı Vercel Deployment
echo =====================================

echo.
echo 📋 Deployment öncesi kontroller...

REM Check if vercel is installed
vercel --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Vercel CLI yüklü değil!
    echo    npm install -g vercel
    pause
    exit /b 1
)

echo ✅ Vercel CLI hazır

REM Check project structure
if not exist "api\search.py" (
    echo ❌ API dosyası bulunamadı!
    pause
    exit /b 1
)

if not exist "frontend\index.html" (
    echo ❌ Frontend dosyası bulunamadı!
    pause
    exit /b 1
)

if not exist "vercel.json" (
    echo ❌ Vercel config bulunamadı!
    pause
    exit /b 1
)

echo ✅ Proje dosyları hazır

echo.
echo 🔐 Vercel login...
vercel login

echo.
echo 🚀 Production deployment başlatılıyor...
echo    Domain: ilacasistan.vercel.app
echo    Framework: Other
echo    Root: ./
echo.

vercel --prod

echo.
echo ✅ Deployment tamamlandı!
echo 🌐 Site: https://ilacasistan.vercel.app
echo 📊 Health: https://ilacasistan.vercel.app/api/health
echo 🔍 Search: https://ilacasistan.vercel.app/api/search?q=paracetamol

echo.
echo 🧪 Test yapmak için:
echo    python test_deployment.py

pause