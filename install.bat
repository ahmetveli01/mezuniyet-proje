@echo off
echo ========================================
echo   Hayvan Turu Tespit Projesi Kurulumu
echo ========================================
echo.

echo 1. Mevcut paketleri kaldırılıyor...
pip uninstall tensorflow keras -y

echo.
echo 2. Gerekli paketler yükleniyor...
pip install Flask==3.0.0
pip install Pillow==10.1.0
pip install numpy==1.26.2

echo.
echo 3. TensorFlow yükleniyor (bu biraz zaman alabilir)...
pip install tensorflow==2.15.0

echo.
echo 4. Kurulum tamamlandı!
echo.
echo Uygulamayı başlatmak için: python main.py
echo Tarayıcıda: http://localhost:8000
echo.
pause
