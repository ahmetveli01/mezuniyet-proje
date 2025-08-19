from flask import Flask, request, jsonify, send_from_directory
import os
import logging

app = Flask(__name__)

# Import required packages
try:
    from PIL import Image, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Try to load TensorFlow model
try:
    from keras.models import load_model
    from tensorflow.keras.layers import DepthwiseConv2D as KerasDepthwiseConv2D
    
    class CustomDepthwiseConv2D(KerasDepthwiseConv2D):
        def __init__(self, *args, **kwargs):
            kwargs.pop('groups', None)
            super().__init__(*args, **kwargs)
    
    model = load_model(r'D:\KODLAND\OgrenciProjeleri\KodlandAhmetVeli\keras_model.h5', 
                      custom_objects={'DepthwiseConv2D': CustomDepthwiseConv2D}, 
                      compile=False)
    MODEL_AVAILABLE = True
    print("✅ Model başarıyla yüklendi")
        
except Exception as e:
    print(f"⚠️ Model yüklenemedi: {e}")
    model = None
    MODEL_AVAILABLE = False

# Load labels
try:
    with open(r"D:\KODLAND\OgrenciProjeleri\KodlandAhmetVeli\labels.txt", "r", encoding='utf-8') as f:
        # Sayıları kaldır ve sadece hayvan isimlerini al
        class_names = []
        for line in f.readlines():
            line = line.strip()
            # Sayı ve boşluktan sonraki kısmı al (hayvan ismi)
            if line and ' ' in line:
                animal_name = line.split(' ', 1)[1]  # İlk boşluktan sonrasını al
                class_names.append(animal_name)
            elif line:  # Sadece hayvan ismi varsa
                class_names.append(line)
    print(f"✅ {len(class_names)} sınıf yüklendi")
except Exception as e:
    print(f"⚠️ Labels yüklenemedi: {e}")
    class_names = list(ANIMAL_INFO.keys())

# Hayvan bilgileri sözlüğü
ANIMAL_INFO = {
    "Aslan": {
        "bilimsel_ad": "Panthera leo",
        "aile": "Kedigiller (Felidae)",
        "habitat": "Afrika savanları ve Hindistan'ın Gir Ormanı",
        "beslenme": "Etçil - zebra, antilop, bufalo avlar",
        "özellikler": "Erkek aslanlar yele sahiptir, sosyal hayvanlardır",
        "tehlike_durumu": "Hassas tür",
        "ilginç_bilgi": "Aslanlar günde 20 saat uyuyabilir!",
        "yaşam_süresi": "10-14 yıl (vahşi doğada)",
        "ağırlık": "Erkek: 150-250 kg, Dişi: 120-180 kg"
    },
    "Kartal": {
        "bilimsel_ad": "Aquila chrysaetos",
        "aile": "Atmacagiller (Accipitridae)",
        "habitat": "Dağlık bölgeler, ormanlar, açık alanlar",
        "beslenme": "Etçil - tavşan, fare, kuş avlar",
        "özellikler": "Keskin görüş, güçlü pençeler, yüksekten avlanma",
        "tehlike_durumu": "Korunmaya muhtaç",
        "ilginç_bilgi": "Kartallar 3-4 km yükseklikten avını görebilir!",
        "yaşam_süresi": "20-30 yıl",
        "ağırlık": "3-7 kg"
    },
    "Çita": {
        "bilimsel_ad": "Acinonyx jubatus",
        "aile": "Kedigiller (Felidae)",
        "habitat": "Afrika savanları ve İran'da",
        "beslenme": "Etçil - antilop, ceylan, tavşan",
        "özellikler": "Dünyanın en hızlı kara hayvanı",
        "tehlike_durumu": "Hassas tür",
        "ilginç_bilgi": "Çita saatte 110 km hıza ulaşabilir!",
        "yaşam_süresi": "8-12 yıl",
        "ağırlık": "35-65 kg"
    },
    "Armadillo": {
        "bilimsel_ad": "Dasypus novemcinctus",
        "aile": "Armadillogiller (Dasypodidae)",
        "habitat": "Amerika kıtasında, çöller ve ormanlar",
        "beslenme": "Böcekçil - böcek, solucan, küçük omurgasızlar",
        "özellikler": "Zırh benzeri plakalar, toprak kazma uzmanı",
        "tehlike_durumu": "En az endişe",
        "ilginç_bilgi": "Armadillolar suda yürüyebilir ve nefesini 6 dakika tutabilir!",
        "yaşam_süresi": "12-15 yıl",
        "ağırlık": "2-15 kg"
    },
    "Fil": {
        "bilimsel_ad": "Loxodonta africana",
        "aile": "Filgiller (Elephantidae)",
        "habitat": "Afrika savanları ve ormanları",
        "beslenme": "Otçul - ot, yaprak, meyve, ağaç kabuğu",
        "özellikler": "En büyük kara memelisi, uzun hortum",
        "tehlike_durumu": "Tehlikede",
        "ilginç_bilgi": "Filler ölülerini hatırlar ve yas tutar!",
        "yaşam_süresi": "60-70 yıl",
        "ağırlık": "3,000-6,000 kg"
    },
    "Tekir_Kedi": {
        "bilimsel_ad": "Felis catus",
        "aile": "Kedigiller (Felidae)",
        "habitat": "Evcil hayvan, dünya çapında",
        "beslenme": "Etçil - kedi maması, et, balık",
        "özellikler": "Evcil, oyuncu, bağımsız",
        "tehlike_durumu": "Evcil hayvan",
        "ilginç_bilgi": "Kediler 200'den fazla ses çıkarabilir!",
        "yaşam_süresi": "12-18 yıl",
        "ağırlık": "3-6 kg"
    },
    "Kopek": {
        "bilimsel_ad": "Canis lupus familiaris",
        "aile": "Köpekgiller (Canidae)",
        "habitat": "Evcil hayvan, dünya çapında",
        "beslenme": "Etçil - köpek maması, et, sebze",
        "özellikler": "Sadık, zeki, sosyal",
        "tehlike_durumu": "Evcil hayvan",
        "ilginç_bilgi": "Köpekler insanların duygularını anlayabilir!",
        "yaşam_süresi": "10-15 yıl",
        "ağırlık": "1-50 kg (ırka göre)"
    },
    "Muhabbet_Kusu": {
        "bilimsel_ad": "Melopsittacus undulatus",
        "aile": "Papağangiller (Psittacidae)",
        "habitat": "Avustralya'da açık alanlar ve ormanlar",
        "beslenme": "Otçul - tohum, meyve, çiçek",
        "özellikler": "Renkli tüyler, konuşabilir, sosyal",
        "tehlike_durumu": "En az endişe",
        "ilginç_bilgi": "Muhabbet kuşları 1000'den fazla kelime öğrenebilir!",
        "yaşam_süresi": "5-10 yıl",
        "ağırlık": "30-40 gram"
    },
    "Boz_Ayi": {
        "bilimsel_ad": "Ursus arctos",
        "aile": "Ayıgiller (Ursidae)",
        "habitat": "Kuzey Amerika, Avrupa ve Asya ormanları",
        "beslenme": "Hepçil - et, balık, meyve, bitki",
        "özellikler": "Güçlü, kış uykusuna yatar, iyi yüzücü",
        "tehlike_durumu": "En az endişe",
        "ilginç_bilgi": "Boz ayılar 800 kg ağırlığa ulaşabilir!",
        "yaşam_süresi": "20-30 yıl",
        "ağırlık": "200-800 kg"
    },
    "Kurt": {
        "bilimsel_ad": "Canis lupus",
        "aile": "Köpekgiller (Canidae)",
        "habitat": "Ormanlar, tundralar, dağlar",
        "beslenme": "Etçil - geyik, tavşan, küçük memeliler",
        "özellikler": "Sosyal, zeki, sürü halinde yaşar",
        "tehlike_durumu": "Hassas tür",
        "ilginç_bilgi": "Kurtlar 65 km/s hızla koşabilir!",
        "yaşam_süresi": "6-8 yıl",
        "ağırlık": "30-80 kg"
    },
    "Tilki": {
        "bilimsel_ad": "Vulpes vulpes",
        "aile": "Köpekgiller (Canidae)",
        "habitat": "Ormanlar, çayırlar, şehirler",
        "beslenme": "Hepçil - küçük hayvanlar, meyve, böcek",
        "özellikler": "Kurnaz, hızlı, gece aktif",
        "tehlike_durumu": "En az endişe",
        "ilginç_bilgi": "Tilki sesleri 40 farklı türde çıkarabilir!",
        "yaşam_süresi": "2-5 yıl",
        "ağırlık": "3-14 kg"
    },
    "Fare": {
        "bilimsel_ad": "Mus musculus",
        "aile": "Faregiller (Muridae)",
        "habitat": "Dünya çapında, şehirler ve kırsal alanlar",
        "beslenme": "Hepçil - tohum, böcek, et artıkları",
        "özellikler": "Küçük, hızlı, üretken",
        "tehlike_durumu": "En az endişe",
        "ilginç_bilgi": "Fareler günde 25 kez idrar yapabilir!",
        "yaşam_süresi": "1-3 yıl",
        "ağırlık": "10-25 gram"
    },
    "Bukalemun": {
        "bilimsel_ad": "Chamaeleonidae",
        "aile": "Bukalemungiller (Chamaeleonidae)",
        "habitat": "Afrika, Madagaskar, güney Avrupa",
        "beslenme": "Böcekçil - böcek, örümcek, küçük omurgasızlar",
        "özellikler": "Renk değiştirme, uzun dil, gözleri bağımsız hareket eder",
        "tehlike_durumu": "Hassas tür",
        "ilginç_bilgi": "Bukalemun dili vücudunun 2 katı uzunluğa çıkabilir!",
        "yaşam_süresi": "2-10 yıl",
        "ağırlık": "85-170 gram"
    },
    "Panda": {
        "bilimsel_ad": "Ailuropoda melanoleuca",
        "aile": "Ayıgiller (Ursidae)",
        "habitat": "Çin'in bambu ormanları",
        "beslenme": "Otçul - bambu yaprakları ve sürgünleri",
        "özellikler": "Siyah-beyaz tüy, bambu sevgisi",
        "tehlike_durumu": "Tehlikede",
        "ilginç_bilgi": "Pandalar günde 14 kg bambu yiyebilir!",
        "yaşam_süresi": "20-30 yıl",
        "ağırlık": "80-120 kg"
    },
    "Kaplumbaga": {
        "bilimsel_ad": "Testudines",
        "aile": "Kaplumbağagiller (Testudinidae)",
        "habitat": "Karada, tatlı suda ve denizde",
        "beslenme": "Hepçil - bitki, böcek, küçük hayvanlar",
        "özellikler": "Kabuk koruması, uzun yaşam, yavaş hareket",
        "tehlike_durumu": "Hassas tür",
        "ilginç_bilgi": "Kaplumbağalar 150 yıldan fazla yaşayabilir!",
        "yaşam_süresi": "50-150 yıl",
        "ağırlık": "0.5-300 kg (türe göre)"
    },
    "Kanguru": {
        "bilimsel_ad": "Macropodidae",
        "aile": "Kangurugiller (Macropodidae)",
        "habitat": "Avustralya'da açık alanlar ve ormanlar",
        "beslenme": "Otçul - ot, yaprak, çiçek",
        "özellikler": "Zıplama, keseli, güçlü kuyruk",
        "tehlike_durumu": "En az endişe",
        "ilginç_bilgi": "Kangurular 9 metre zıplayabilir!",
        "yaşam_süresi": "6-20 yıl",
        "ağırlık": "20-90 kg"
    },
    "Ahtapot": {
        "bilimsel_ad": "Octopoda",
        "aile": "Ahtapotgiller (Octopodidae)",
        "habitat": "Denizlerde, kayalık diplerinde",
        "beslenme": "Etçil - yengeç, istiridye, balık",
        "özellikler": "8 kollu, mürekkep püskürtme, zeki",
        "tehlike_durumu": "Hassas tür",
        "ilginç_bilgi": "Ahtapotlar 3 kalbe sahiptir!",
        "yaşam_süresi": "1-5 yıl",
        "ağırlık": "0.5-50 kg"
    },
    "Sirtlan": {
        "bilimsel_ad": "Hyaenidae",
        "aile": "Sırtlangiller (Hyaenidae)",
        "habitat": "Afrika savanları ve ormanları",
        "beslenme": "Etçil - leş, avlanan hayvanlar",
        "özellikler": "Güçlü çene, sosyal, gülme sesi",
        "tehlike_durumu": "Hassas tür",
        "ilginç_bilgi": "Sırtlanlar kemikleri bile kırabilir!",
        "yaşam_süresi": "12-25 yıl",
        "ağırlık": "40-86 kg"
    },
    "Kugu": {
        "bilimsel_ad": "Cygnus olor",
        "aile": "Ördekgiller (Anatidae)",
        "habitat": "Göller, nehirler, kıyılar",
        "beslenme": "Otçul - su bitkileri, alg, küçük omurgasızlar",
        "özellikler": "Beyaz tüy, uzun boyun, zarif yüzme",
        "tehlike_durumu": "En az endişe",
        "ilginç_bilgi": "Kuğular ömür boyu tek eşli yaşar!",
        "yaşam_süresi": "10-20 yıl",
        "ağırlık": "8-15 kg"
    },
    "Kirpi": {
        "bilimsel_ad": "Erinaceinae",
        "aile": "Kirpigiller (Erinaceidae)",
        "habitat": "Ormanlar, çayırlar, bahçeler",
        "beslenme": "Böcekçil - böcek, solucan, küçük omurgasızlar",
        "özellikler": "Dikenli tüyler, top yuvarlanma",
        "tehlike_durumu": "En az endişe",
        "ilginç_bilgi": "Kirpiler 5000-7000 dikene sahiptir!",
        "yaşam_süresi": "2-7 yıl",
        "ağırlık": "0.5-2 kg"
    },
    "Lemur": {
        "bilimsel_ad": "Lemuriformes",
        "aile": "Lemurgiller (Lemuridae)",
        "habitat": "Madagaskar ormanları",
        "beslenme": "Hepçil - meyve, yaprak, böcek",
        "özellikler": "Uzun kuyruk, sosyal, ağaçta yaşar",
        "tehlike_durumu": "Tehlikede",
        "ilginç_bilgi": "Lemurlar güneşe karşı yoga yapar!",
        "yaşam_süresi": "15-20 yıl",
        "ağırlık": "0.5-9 kg"
    },
    "Yunus": {
        "bilimsel_ad": "Delphinidae",
        "aile": "Yunusgiller (Delphinidae)",
        "habitat": "Okyanuslar ve denizler",
        "beslenme": "Etçil - balık, kalamar, kabuklular",
        "özellikler": "Zeki, sosyal, ekolokasyon",
        "tehlike_durumu": "Hassas tür",
        "ilginç_bilgi": "Yunuslar uyurken tek gözü açık kalır!",
        "yaşam_süresi": "20-50 yıl",
        "ağırlık": "50-650 kg"
    },
    "Goril": {
        "bilimsel_ad": "Gorilla",
        "aile": "İnsansı maymunlar (Hominidae)",
        "habitat": "Afrika ormanları",
        "beslenme": "Otçul - yaprak, meyve, bitki",
        "özellikler": "Güçlü, zeki, sosyal, insana en yakın",
        "tehlike_durumu": "Tehlikede",
        "ilginç_bilgi": "Goriller insan DNA'sının %98'ini paylaşır!",
        "yaşam_süresi": "35-50 yıl",
        "ağırlık": "100-200 kg"
    },
    "Horoz": {
        "bilimsel_ad": "Gallus gallus domesticus",
        "aile": "Sülüngiller (Phasianidae)",
        "habitat": "Çiftlikler, köyler, dünya çapında",
        "beslenme": "Hepçil - tohum, böcek, küçük hayvanlar",
        "özellikler": "Renkli tüyler, ötüş, sosyal",
        "tehlike_durumu": "Evcil hayvan",
        "ilginç_bilgi": "Horozlar güneş doğmadan önce öter!",
        "yaşam_süresi": "5-10 yıl",
        "ağırlık": "2-4 kg"
    },
    "Kogala": {
        "bilimsel_ad": "Phascolarctos cinereus",
        "aile": "Kogalagiller (Phascolarctidae)",
        "habitat": "Avustralya'nın doğu kıyıları",
        "beslenme": "Otçul - okaliptüs yaprakları",
        "özellikler": "Gri tüy, keseli, ağaçta yaşar",
        "tehlike_durumu": "Tehlikede",
        "ilginç_bilgi": "Kogalalar günde 22 saat uyur!",
        "yaşam_süresi": "13-18 yıl",
        "ağırlık": "4-15 kg"
    },
    "At": {
        "bilimsel_ad": "Equus caballus",
        "aile": "Atgiller (Equidae)",
        "habitat": "Çiftlikler, çayırlar, dünya çapında",
        "beslenme": "Otçul - ot, saman, yulaf",
        "özellikler": "Güçlü, hızlı, sosyal, evcil",
        "tehlike_durumu": "Evcil hayvan",
        "ilginç_bilgi": "Atlar ayakta uyuyabilir!",
        "yaşam_süresi": "25-30 yıl",
        "ağırlık": "400-1000 kg"
    },
    "Ornitorenk": {
        "bilimsel_ad": "Ornithorhynchus anatinus",
        "aile": "Ornitorenkgiller (Ornithorhynchidae)",
        "habitat": "Avustralya'nın doğu kıyıları",
        "beslenme": "Etçil - böcek, solucan, küçük omurgasızlar",
        "özellikler": "Gaga, yumurta bırakır, zehirli",
        "tehlike_durumu": "Tehlikede",
        "ilginç_bilgi": "Ornitorenkler elektrik algılayabilir!",
        "yaşam_süresi": "10-20 yıl",
        "ağırlık": "0.7-2.4 kg"
    },
    "Deve_Kusu": {
        "bilimsel_ad": "Struthio camelus",
        "aile": "Deve kuşugiller (Struthionidae)",
        "habitat": "Afrika savanları",
        "beslenme": "Hepçil - bitki, böcek, küçük hayvanlar",
        "özellikler": "Dünyanın en büyük kuşu, uçamaz",
        "tehlike_durumu": "En az endişe",
        "ilginç_bilgi": "Deve kuşları saatte 70 km koşabilir!",
        "yaşam_süresi": "30-40 yıl",
        "ağırlık": "90-130 kg"
    },
    "Hipopotam": {
        "bilimsel_ad": "Hippopotamus amphibius",
        "aile": "Hipopotamgiller (Hippopotamidae)",
        "habitat": "Afrika'da nehirler ve göller",
        "beslenme": "Otçul - ot, su bitkileri",
        "özellikler": "Büyük, suda yaşar, agresif",
        "tehlike_durumu": "Hassas tür",
        "ilginç_bilgi": "Hipopotamlar günde 50 kg ot yiyebilir!",
        "yaşam_süresi": "40-50 yıl",
        "ağırlık": "1,500-3,200 kg"
    },
    "Aksolotl": {
        "bilimsel_ad": "Ambystoma mexicanum",
        "aile": "Semendergiller (Ambystomatidae)",
        "habitat": "Meksika'da Xochimilco Gölü",
        "beslenme": "Etçil - böcek, solucan, küçük balık",
        "özellikler": "Sucul, solungaçlı, yenilenme yeteneği",
        "tehlike_durumu": "Kritik tehlikede",
        "ilginç_bilgi": "Aksolotllar vücut parçalarını yeniden üretebilir!",
        "yaşam_süresi": "10-15 yıl",
        "ağırlık": "60-110 gram"
    }
}

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_image(image):
    """Resmi model için hazırlar"""
    if not PIL_AVAILABLE or not NUMPY_AVAILABLE:
        return None
        
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS).convert("RGB")
    image_array = np.asarray(image)
    normalized = (image_array.astype(np.float32) / 127.5) - 1
    data = np.expand_dims(normalized, axis=0)
    return data

def demo_predict():
    """Demo tahmin - gerçek model yoksa"""
    import random
    # Tüm hayvanlardan rastgele seç
    demo_animals = list(ANIMAL_INFO.keys())
    return random.choice(demo_animals), random.uniform(0.7, 0.95)

def get_animal_info(animal_name):
    """Hayvan adına göre bilgi döndürür"""
    # Labels.txt'deki isimleri ANIMAL_INFO'daki anahtarlarla eşleştir
    if animal_name in ANIMAL_INFO:
        return ANIMAL_INFO[animal_name]
    else:
        # Genel bilgi
        return {
            "bilimsel_ad": "Bilinmiyor",
            "aile": "Bilinmiyor",
            "habitat": "Bilinmiyor",
            "beslenme": "Bilinmiyor",
            "özellikler": "Bu hayvan hakkında detaylı bilgi bulunamadı",
            "tehlike_durumu": "Bilinmiyor",
            "ilginç_bilgi": "Bu hayvan hakkında daha fazla bilgi için araştırma yapabilirsiniz",
            "yaşam_süresi": "Bilinmiyor",
            "ağırlık": "Bilinmiyor"
        }

@app.route('/')
def index():
    """Ana sayfa"""
    return send_from_directory('.', 'index.html')

@app.route('/game')
def game():
    """Oyun sayfası"""
    return send_from_directory('.', 'game.html')

@app.route('/health')
def health_check():
    """Sağlık kontrolü endpoint'i"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': MODEL_AVAILABLE,
        'classes_count': len(class_names),
        'message': 'Hayvan türü tespit API çalışıyor',
        'mode': 'demo' if not MODEL_AVAILABLE else 'production'
    })

@app.route('/classes')
def get_classes():
    """Mevcut sınıfları listeler"""
    return jsonify({
        'classes': class_names,
        'count': len(class_names)
    })

@app.route('/animal_info/<animal_name>')
def animal_info(animal_name):
    """Belirli bir hayvan hakkında bilgi döndürür"""
    info = get_animal_info(animal_name)
    return jsonify({
        'animal': animal_name,
        'info': info
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Resim tahmin endpoint'i"""
    if not PIL_AVAILABLE:
        return jsonify({'error': 'Pillow yüklenemedi'}), 500
        
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya yüklenmedi'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    # Dosya türü kontrolü
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    if not file.filename.lower().rsplit('.', 1)[1] in allowed_extensions:
        return jsonify({'error': 'Desteklenmeyen dosya türü'}), 400

    # Resmi aç
    image = Image.open(file.stream)
    print(f"📸 Resim yüklendi: {file.filename}")
    
    if MODEL_AVAILABLE and model:
        # Gerçek model ile tahmin
        data = preprocess_image(image)
        if data is None:
            return jsonify({'error': 'Resim işlenemedi'}), 400
        
        prediction = model.predict(data, verbose=0)
        index = np.argmax(prediction)
        confidence = float(prediction[0][index])
        class_name = class_names[index] if index < len(class_names) else 'Bilinmeyen'
        
        print(f"🎯 Tahmin: {class_name} (güven: {confidence:.3f})")
        
        # Hayvan bilgilerini ekle
        animal_info = get_animal_info(class_name)
        
        return jsonify({
            'class': class_name, 
            'confidence': confidence,
            'filename': file.filename,
            'mode': 'production',
            'animal_info': animal_info
        })
    else:
        # Demo tahmin
        class_name, confidence = demo_predict()
        print(f"🎲 Demo tahmin: {class_name} (güven: {confidence:.3f})")
        
        # Demo için de hayvan bilgilerini ekle
        animal_info = get_animal_info(class_name)
        
        return jsonify({
            'class': class_name, 
            'confidence': confidence,
            'filename': file.filename,
            'mode': 'demo',
            'message': 'Bu bir demo tahmindir',
            'animal_info': animal_info
        })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Sayfa bulunamadı'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Sunucu hatası'}), 500

if __name__ == "__main__":
    print("🚀 Flask uygulaması başlatılıyor...")
    
    if not MODEL_AVAILABLE:
        print("⚠️ Demo modunda çalışacak")
    
    app.run(debug=True, port=8000, host='0.0.0.0')

