import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk

# NLTK stopwords veritabanını indir
nltk.download('stopwords')#Gereksiz kelimeler
nltk.download('punkt')#Cümle ayırıcı


# Veriyi yükle
def load_and_process_data(csv_path):
    data = pd.read_csv(csv_path)
    data1 = data[['name', 'rating', 'user_ratings_total', 'formatted_address', 'review_rating', 'review_text']]
    data1.dropna(inplace=True)
    data1.loc[:, 'popularity_score'] = data1['user_ratings_total'] * data1['rating']
    data1['average_review_rating'] = data1.groupby('name')['review_rating'].transform('mean')#Aynı kafe için yapılan yorumların ortalama puanını hesaplar.
    return data1


# Metin temizleme ve stopwords (gereksiz kelimeler) kaldırma
def process_review(text, ps, stop):
    text = re.sub("[^a-zA-Z]", " ", text)  # Yalnızca harfler
    text = text.lower()  # Küçük harfe çevir
    text = text.split()  # Kelimelere ayır
    text = [ps.stem(word) for word in text if word not in stop]  # Stopwords kaldır ve kök haline getir
    return " ".join(text)


# Yorumları işleyip 'processed_review_text' sütununa ekleyelim
def preprocess_reviews(data1):
    ps = PorterStemmer()
    stop = set(stopwords.words("english"))
    data1['processed_review_text'] = data1['review_text'].apply(lambda x: process_review(x, ps, stop))
    return data1



def vectorize_reviews(data1):
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(data1['processed_review_text'])
    return vectorizer, X


# LDA modelini kur, metin verileri (X) kullanılarak model eğitilir.
def train_lda_model(X, n_topics=5):
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=0)
    lda.fit(X)
    return lda


# LDA modelinin her konusundaki en yüksek sıklığa sahip kelimeleri gösterir.
def print_topics(model, vectorizer, n_words=10):
    words = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        topic_words = " ".join([words[i] for i in topic.argsort()[:-n_words - 1:-1]])
        topics.append(topic_words)
    return topics


# Bir yorumun hangi konuya ait olduğunu bulma
def get_topic_for_review(text, vectorizer, lda):
    text_vec = vectorizer.transform([text])  # Yorumun vektöre dönüşmesi
    topic = lda.transform(text_vec)  # LDA modeline göre konuyu tahmin et, yorumun hangi konulara ait olduğunun olasılıklarını hesaplar.
    return topic.argmax()  # En yüksek olasılıkla ilişkilendirilmiş konu dönderiliyor


# Anahtar kelimelere göre kafe öneriliyor burada
def get_cafes_by_topic(data1, topic_number, vectorizer, lda):
    topic_cafes = data1[
        data1['processed_review_text'].apply(lambda x: get_topic_for_review(x, vectorizer, lda) == topic_number)]
    if not topic_cafes.empty:
        cafes = topic_cafes['name'].tolist()
    else:
        cafes = []
    return cafes


# Kullanıcıya sık kullanılan pozitif kelimeleri önerme
def get_suggested_positive_keywords(data1):
    all_reviews = " ".join(data1['processed_review_text'])
    words = all_reviews.split()
    word_freq = pd.Series(words).value_counts()
    positive_keywords = word_freq.head(10).index.tolist()
    return positive_keywords


# Kullanıcıya pozitif kelimelere göre kafe önerisi
def get_cafes_by_positive_keyword(keyword, data1):
    if isinstance(keyword, str):
        keyword = keyword.lower()  # Kelimeyi küçük harfe çevir
    else:
        raise ValueError("keyword parametresi bir string olmalıdır.")

    keyword = keyword.lower()
    filtered_cafes = set()
    for index, row in data1.iterrows():
        if keyword in row['processed_review_text'].lower():
            filtered_cafes.add(row['name'])
    return filtered_cafes


# Kullanıcıya sık kullanılan pozitif kelimeleri öneriyor ve kelime seçtiriyor
def suggest_positive_keywords(data1):
    print("İşte sık kullanılan pozitif kelimeler:")
    positive_keywords = get_suggested_positive_keywords(data1)
    for idx, word in enumerate(positive_keywords, 1):
        print(f"{idx}. {word}")

    while True:
        user_input = input(
            "Lütfen yukarıdaki listeden bir numara girerek bir kelime seçin veya bir kelime yazın: ").strip().lower()

        if user_input in positive_keywords:
            return user_input
        elif user_input.isalpha():
            return user_input
        else:
            print(
                "Geçersiz kelime! Lütfen yukarıdaki listedeki kelimelerden birini seçin veya geçerli bir kelime yazın.")


# Kullanıcıya pozitif kelimelere göre kafe öneriyorr
def get_cafes_by_selected_keyword(data1):
    # Pozitif anahtar kelimeleri öner
    keyword = suggest_positive_keywords(data1)

    # Anahtar kelimeye göre kafeleri al
    cafes = get_cafes_by_positive_keyword(data1, keyword)

    # Kafeler varsa, bunları bir listeye ekleyip döndürelim
    cafe_list = []

    if cafes:
        print(f"'{keyword}' kelimesi ile ilgili kafeler:")
        for cafe in cafes:
            cafe_list.append(cafe)  # Kafeyi listeye ekle
            print(f"- {cafe}")
    else:
        print(f"'{keyword}' kelimesi ile ilgili kafe bulunamadı.")

    return cafe_list  # Listeyi döndür


# get_model fonksiyonu
def get_model(csv_path, n_topics=5):
    # Veriyi yükle ve işle
    data1 = load_and_process_data(csv_path)
    data1 = preprocess_reviews(data1)

    # Yorumları vektörleştir
    vectorizer, X = vectorize_reviews(data1)

    # LDA modelini eğit
    lda = train_lda_model(X, n_topics)

    # Modeli ve vektörleştiriciyi döndür
    return lda, vectorizer, data1


# Burası ana akış burada get_model fonksiyonunu çağırarak modeli oluşturur ve ardından kullanıcıya kafe önerilerini sunuyor
def main(csv_path):
    lda, vectorizer, data1 = get_model(csv_path)  # get_model fonksiyonunu çağırıyoruz

    print("Kafe önerileri yapılacak...\n")
    get_cafes_by_selected_keyword(data1)


if __name__ == "__main__":
    csv_path = "C:/Users/Cansel/Documents/malatya_kafe_detaylari1.csv"  # CSV dosyasının yolu
    main(csv_path)