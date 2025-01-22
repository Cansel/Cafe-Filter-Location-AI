

#zbsv zyde dmvy marw uygulama şifresi gmaili bağlamak için
from flask_mail import Mail, Message
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from app.models.topic_modeling import get_model, get_suggested_positive_keywords, get_cafes_by_positive_keyword, print_topics

app = Flask(__name__)

# Flask-Mail Yapılandırması
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'tastelocator@gmail.com'
app.config['MAIL_PASSWORD'] = 'zbsv zyde dmvy marw'
app.config['MAIL_DEFAULT_SENDER'] = 'tastelocator@gmail.com'

mail = Mail(app)


# MongoDB Bağlantısı
connection_string = "mongodb+srv://ayse:aysemongo@cluster0.1y4yo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)

# Bağlantıyı kontrol etme
try:
    db = client["kafe"]  # 'kafe' veritabanına bağlanıyoruz
    user_collection = db["kullanici"]  # 'kullanici' koleksiyonuna bağlanıyoruz
    cafe_collection = db["cafes"]  # 'cafes' koleksiyonuna bağlanıyoruz
    print("Veritabanına başarılı bir şekilde bağlanıldı!")
except Exception as e:
    print("Veritabanına bağlanırken bir hata oluştu:", e)

app.secret_key = 'supersecretkey'  #Flask, flash mesajlar ve oturumlar gibi işlemler için bir anahtara ihtiyaç duyar. Bu anahtar burada tanımlanmış.
bcrypt = Bcrypt(app)                #Şifrelerin güvenli bir şekilde saklanmasını sağlamak için bcrypt kütüphanesi kullanılır.
jwt = JWTManager(app)                #Kullanıcı doğrulama işlemleri için JWT (JSON Web Token) kullanılır.

# # Anasayfa yönlendirmesi
# @app.route('/')
# def home():
#     return render_template('index.html')

# Anasayfa Rotası
@app.route('/')
def home():
    return render_template('index.html')

# İletişim Formu Gönderme Rotası
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    message_content = request.form['message']

    msg = Message(
        subject=f"Yeni İletişim Mesajı - {name}",
        sender=app.config['MAIL_USERNAME'],
        recipients=['ayseats44@gmail.com'],  # Mesajı alacak e-posta adresi
        body=f"Ad: {name}\nE-posta: {email}\nMesaj:\n{message_content}"
    )
    mail.send(msg)

    return "Mesajınız başarıyla gönderildi. Teşekkür ederiz!"
# # Giriş sayfası yönlendirmesi
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # MongoDB'de kullanıcıyı buluyoruz
        user = user_collection.find_one({'username': username})

        if user and user['password'] == password:  # Şifreyi hash'lemeden kontrol ediyoruz
            # Başarılı giriş, JWT token oluştur
            access_token = create_access_token(identity=str(user['_id']))
            return redirect(url_for('detay'))  # Giriş başarılıysa ana sayfaya yönlendirme,JWT token oluşturulur ve detay sayfasına yönlendirilir.
        else:
            flash("Geçersiz kullanıcı adı veya şifre", "danger")
    return render_template('login.html')


# Kayıt sayfası yönlendirmesi
#Kullanıcı adı ve şifre ile kayıt işlemi yapılır. Şifreler eşleşiyorsa kullanıcı veritabanına kaydedilir.
#Kayıt başarılıysa, kullanıcıyı giriş sayfasına yönlendirir. Hata durumunda, kullanıcıya hata mesajı gösterilir.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # Şifrelerin eşleştiğini kontrol ediyoruz
        if password != confirm_password:
            flash("Şifreler uyuşmuyor!", "danger")
            return render_template('register.html')

        # Kullanıcıyı eklemeye çalışıyoruz
        user_data = {"username": username, "password": password}
        result = user_collection.insert_one(user_data)

        if result.inserted_id:
            flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
            return render_template('login.html')
        else:
            flash("Kayıt sırasında bir hata oluştu.", "danger")
            return render_template('register.html')

    return render_template('register.html')
#
# Flask route içinde POST isteği kontrolü
# Detay sayfası
@app.route('/detay', methods=['GET', 'POST'])
def detay():
    file_path = "C:/Users/Cansel/Documents/malatya_kafe_detaylari1.csv"
    lda, vectorizer, data1 = get_model(file_path)
    positive_keywords = get_suggested_positive_keywords(data1)
    topics = print_topics(lda, vectorizer)

    if request.method == 'POST':
        comment = request.form.get("comment", "").strip()
        rating = request.form.get("rating", "").strip()
        keyword = request.form.get("filter-keywords", "").strip()

        if comment and rating:
            comment_data = {
                'comment': comment,
                'rating': rating,
                'keyword': keyword,
                'timestamp': datetime.now()  # Yorumun zaman damgası
            }
            try:
                db['comment'].insert_one(comment_data)
                flash("Yorumunuz başarıyla kaydedildi!", "success")
            except Exception as e:
                flash("Yorum kaydedilirken bir hata oluştu.", "danger")
                print("Yorum kaydedilirken hata:", e)

        suggested_cafes = get_cafes_by_positive_keyword(keyword, data1)
        cafes = cafe_collection.find()
        matched_cafes = []
        for suggested_cafe in suggested_cafes:
            for cafe in cafes:
                if suggested_cafe.lower() in cafe['name'].lower():
                    matched_cafes.append({
                        'name': cafe['name'],
                        'latitude': cafe['latitude'],
                        'longitude': cafe['longitude'],
                        'address': cafe['address']
                    })
                    break

        return render_template('detay.html',
                               keywords=positive_keywords,
                               topics=topics,
                               cafes=matched_cafes)

    return render_template('detay.html', keywords=positive_keywords, topics=topics)

if __name__ == '__main__':
    app.run(debug=True)