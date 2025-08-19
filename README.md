# 🐾 Hayvan Türü Tespit Projesi

Bu proje, yapay zeka kullanarak hayvan türlerini tespit eden modern bir web uygulamasıdır. Flask backend'i ve güzel bir HTML/CSS/JavaScript frontend'i ile geliştirilmiştir.

## ✨ Özellikler

- 🎯 **30 farklı hayvan türü** tespit edebilme
- 🖼️ **Drag & Drop** resim yükleme
- 📱 **Responsive tasarım** (mobil uyumlu)
- 🚀 **Hızlı tahmin** (saniyeler içinde)
- 🎨 **Modern ve güzel arayüz**
- 📊 **Güven skoru** gösterimi
- 🔄 **Gerçek zamanlı** sonuçlar

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adım 1: Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 2: Uygulamayı Çalıştırın
```bash
python main.py
```

### Adım 3: Tarayıcıda Açın
```
http://localhost:8000
```

## 📁 Proje Yapısı

```
├── main.py              # Flask backend uygulaması
├── index.html           # Modern frontend arayüzü
├── keras_model.h5       # Eğitilmiş yapay zeka modeli
├── labels.txt           # Hayvan türü etiketleri
├── requirements.txt     # Python paket gereksinimleri
└── README.md           # Bu dosya
```

## 🎯 Desteklenen Hayvan Türleri

Proje şu 30 hayvan türünü tespit edebilir:

- Aslan, Kartal, Çita, Armadillo, Fil
- Tekir Kedi, Köpek, Muhabbet Kuşu, Boz Ayı, Kurt
- Tilki, Fare, Bukalemun, Panda, Kaplumbağa
- Kanguru, Ahtapot, Sırtlan, Kuğu, Kirpi
- Lemur, Yunus, Goril, Horoz, Koala
- At, Ornitorenk, Deve Kuşu, Hipopotam, Aksolotl

## 🔧 API Endpoints

- `GET /` - Ana sayfa
- `POST /predict` - Resim tahmin endpoint'i
- `GET /health` - Sistem sağlık kontrolü
- `GET /classes` - Desteklenen sınıfları listele

## 💻 Kullanım

1. **Resim Yükleyin**: Resmi sürükleyip bırakın veya tıklayarak seçin
2. **Tahmin Bekleyin**: Yapay zeka resmi analiz eder
3. **Sonucu Görün**: Hayvan türü ve güven skoru gösterilir

## 🎨 Teknolojiler

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **AI Model**: TensorFlow/Keras
- **Styling**: CSS Grid, Flexbox, Animations
- **Icons**: Font Awesome

## 🔍 Hata Ayıklama

Eğer uygulama çalışmazsa:

1. **Port kontrolü**: 8000 portunun boş olduğundan emin olun
2. **Model dosyası**: `keras_model.h5` dosyasının mevcut olduğunu kontrol edin
3. **Paketler**: Tüm paketlerin yüklendiğinden emin olun
4. **Logs**: Terminal çıktısını kontrol edin

## 📱 Mobil Uyumluluk

Uygulama tüm cihazlarda çalışır:
- 📱 Mobil telefonlar
- 💻 Tabletler  
- 🖥️ Masaüstü bilgisayarlar

## 🚀 Gelecek Özellikler

- [ ] Çoklu resim yükleme
- [ ] Tahmin geçmişi
- [ ] Hayvan bilgileri ve açıklamaları
- [ ] Sosyal medya paylaşımı
- [ ] Offline çalışma modu

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Terminal loglarını kontrol edin
2. Tarayıcı konsolunu kontrol edin
3. GitHub Issues'da sorun bildirin

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

---

**Geliştirici**: Kodland Öğrenci Projesi  
**Tarih**: 2024  
**Versiyon**: 1.0.0
