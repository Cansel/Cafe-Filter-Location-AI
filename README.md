# CafeFinder — Malatya Kafe Keşif Uygulaması (Flask)

> **Durum:** Bu depo içinde uygulama kaynak kodlarıyla birlikte iki sanal ortam klasörü (`venv/`, `myenv/`) de yer alıyor. Çalıştırmadan önce depoyu sadeleştirmeniz önerilir (aşağıya bkz.).

Bu proje, Malatya’daki kafeleri **kullanıcı yorumlarından konu modelleme (LDA)** ve **pozitif anahtar kelime** filtreleriyle analiz edip, seçilen kafeleri **Google Haritalar** üzerinde gösteren bir Flask uygulamasıdır.

## Özellikler

* 🧭 **Flask tabanlı web arayüzü**: `index.html` (tanıtım/landing) ve `detay.html` (analiz + harita) sayfaları.
* 🧠 **NLP & Konu Modelleme (LDA)**: `app/models/topic_modeling.py`

  * Metin temizleme (stopwords, stem)
  * CountVectorizer + LDA ile konu çıkarımı
* 💬 **Pozitif anahtar kelime önerileri ve filtreleme**: kullanıcı odaklı anahtar kelime ile eşleşen kafe/yorumların öne çıkarılması.
* 🗺️ **Google Maps entegrasyonu**: `detay.html` içinde seçilen kafelerin harita üzerinde pinlenmesi.
* 🔐 **(Taslak) Kimlik Doğrulama**: `login.html` / `register.html` şablonları mevcut; akış kısmen yorum satırında ve tamamlanmayı bekliyor.
* 📦 **(Taslak) MongoDB entegrasyonu**: `views.py` içinde yorumlanmış örnek bağlantı/akış; prod’a uygun hale getirilmeli.

## Depo Yapısı

```
project/
├─ app/
│  ├─ __init__.py            # Flask app import köprüsü
│  ├─ views.py               # Router, form işleme, analiz, harita verisi
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ topic_modeling.py   # Metin işleme + LDA konu modeli + keyword yardımcıları
│  └─ templates/
│     ├─ index.html          # Ana sayfa (landing)
│     ├─ detay.html          # Analiz + harita
│     ├─ login.html          # (Taslak) Giriş
│     └─ register.html       # (Taslak) Kayıt
├─ app/static/
│  ├─ css/                   # `default.css`, `detay.css`, `login.css`, `register.css`
│  ├─ fonts/
│  └─ images/                # Banner ve içerik görselleri
├─ venv/                     # (Projeyle birlikte arşivlenmiş sanal ortam)
└─ myenv/                    # (Projeyle birlikte arşivlenmiş ikinci sanal ortam)
```

> **Not:** `venv/` ve `myenv/` klasörleri bu repoda gereksiz yere çok yer kaplıyor ve taşınabilirliği azaltıyor. Sürüm kontrolünde bu klasörlerin yer almaması önerilir (bkz. `.gitignore`).

## Gerekli Kurulumlar

* Python 3.10+ (3.11 önerilir)
* Bağımlılıklar (önerilen minimum):

  * `Flask`
  * `pandas`
  * `numpy`
  * `nltk`
  * `scikit-learn`
  * (opsiyonel) `python-dotenv` — gizli anahtarları `.env` ile yönetmek için

**Örnek `requirements.txt`**

```txt
Flask>=3.0.0
pandas>=2.0.0
numpy>=1.24.0
nltk>=3.8
scikit-learn>=1.3
python-dotenv>=1.0
```

## Hızlı Başlangıç

1. **Sanal ortam oluşturun**

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **NLTK veri indirimi**
   `topic_modeling.py` NLTK stopwords/punkt indirimi yapıyor; ilk çalıştırmada otomatik inecektir. Gerekirse manuel:

```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```

3. **Google Maps API anahtarı**
   `app/templates/detay.html` içinde Google Maps JS kullanılıyor. Güvenli kullanım için `.env` dosyasıyla bir şablon değişkeni üzerinden geçirmek önerilir:

```bash
# .env
GOOGLE_MAPS_API_KEY=YOUR_KEY_HERE
```

Flask tarafında:

```python
# app/views.py (örnek)
from os import getenv
from dotenv import load_dotenv
load_dotenv()
MAPS_KEY = getenv("GOOGLE_MAPS_API_KEY")
return render_template('detay.html', ..., maps_key=MAPS_KEY)
```

ve `detay.html` içinde:

```html
<script src="https://maps.googleapis.com/maps/api/js?key={{ maps_key }}&libraries=places"></script>
```

4. **Uygulamayı çalıştırın**
   Mevcut `app/__init__.py` sadece `from app.views import app` yapıyor. `views.py` içinde Flask uygulaması tanımı **yorum satırında**. Aşağıdaki gibi düzenleyin veya yeni bir `run.py` oluşturun.

**Seçenek A — `views.py` başını aktif edin**

```python
# app/views.py
from flask import Flask, render_template, request
app = Flask(__name__)

# ... mevcut route/logic ...

if __name__ == "__main__":
    app.run(debug=True)
```

**Seçenek B — Ayrı çalıştırma dosyası**

```python
# run.py
from app.views import app

if __name__ == "__main__":
    app.run(debug=True)
```

```bash
python run.py
```

## Veri Beklentisi (Şema)

Kod tarafında aşağıdaki alanlar kullanılıyor. Veri setinizi bu alanları içerecek şekilde hazırlayın (CSV/JSON kabul edilebilir):

| Alan                    | Açıklama                                                                                           |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| `name`                  | Kafe adı                                                                                           |
| `review_text`           | Kullanıcı yorum metni (ham)                                                                        |
| `processed_review_text` | Temizlenmiş/işlenmiş yorum metni (stopwords, stem vs.) – kod üretir veya önceden sağlayabilirsiniz |
| `rating`                | Kafenin puanı (0–5)                                                                                |
| `user_ratings_total`    | Toplam oy/yorum sayısı                                                                             |
| `average_review_rating` | Ortalama yorum puanı (varsa)                                                                       |
| `address`               | Adres metni                                                                                        |
| `latitude`              | Enlem (harita için)                                                                                |
| `longitude`             | Boylam (harita için)                                                                               |

> **İpucu:** `topic_modeling.py` içindeki `load_and_process_data` ve filtreleme fonksiyonlarını veri kolon adlarınıza göre uyarlayabilirsiniz.

## Uygulama Akışı (Özet)

1. **Index**: Proje tanıtımı ve “Detay” sayfasına yönlendirme.
2. **Detay**:

   * Pozitif anahtar kelime önerisi ve/veya kullanıcı seçimli anahtar kelime ile **kafe filtreleme**
   * LDA ile **konu çıkarımı** ve konu terimlerinin listelenmesi
   * Eşleşen kafelerin **haritada gösterimi**
3. **(Opsiyonel) Auth**: `login.html`/`register.html` şablonları mevcut; `Flask-Login` veya JWT akışı planlanabilir.

## Geliştirme Notları & Bilinen Eksikler

* `views.py` içinde bir kısım kod blokları **yorum satırında** ve çalışır hale getirilmesi gerekiyor.
* Veri seti repoya **dahil değil**; örnek CSV eklenmesi önerilir: `data/cafes.csv`.
* Google Maps anahtarı **hard-code edilmemeli**; `.env` ile aktarılmalı.
* `venv/` ve `myenv/` sürüm kontrolüne dahil edilmemelidir.

## Yol Haritası (TODO)

* [ ] `requirements.txt` ekle ve doğrula
* [ ] `run.py` veya düzenlenmiş `views.py` ile **çalışır demo**
* [ ] Örnek veri dosyası: `data/cafes.csv`
* [ ] `Flask-Login` ile **oturum açma/üye ol** akışını tamamlama
* [ ] Harita tarafında **mesafe/sıralama** seçenekleri ("yakınımdakiler", puana göre vs.)
* [ ] LDA konu sayısını ve n-gram/stopwords ayarlarını **konfigüre edilebilir** hale getirme
* [ ] Basit bir **Dockerfile** (+ `docker-compose.yml`)

## Örnek `.gitignore`

```gitignore
# Python
__pycache__/
*.pyc

# Envs
.venv/
venv/
myenv/

# OS/IDE
.DS_Store
.idea/
.vscode/

# Secrets
.env
```

## Lisans

Uygun bir lisans seçiniz (örn. MIT). `LICENSE` dosyası eklemeniz önerilir.

---

**İletişim & Katkı**
Sorularınız ve katkılarınız için PR açabilir veya issue oluşturabilirsiniz. Bu README taslağı, projeyi çalışır hale getirirken güncellenmek üzere hazırlanmıştır.
