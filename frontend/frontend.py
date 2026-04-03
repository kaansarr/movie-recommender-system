import streamlit as st
import requests

st.set_page_config(page_title="Movie Recommender", layout="centered")

st.title("🎬 Movie Recommendation System")
st.markdown("Kullanıcıya göre film önerisi al 👇")

user_id = st.number_input("User ID gir", min_value=1, step=1)

if st.button("🚀 Öneri Getir"):
    url = f"http://127.0.0.1:8000/recommend?user_id={user_id}"
    
    with st.spinner("Öneriler hazırlanıyor..."):
        response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        recommendations = data["recommendations"]

        st.success("Öneriler hazır 🎉")

        # 🔥 skorları normalize etmek için max bul
        scores = [float(movie["score"]) for movie in recommendations]
        max_score = max(scores) if scores else 1

        # 🔥 GRID görünüm
        cols = st.columns(2)

        for i, movie in enumerate(recommendations):
            with cols[i % 2]:
                score = float(movie["score"])
                normalized_score = score / max_score if max_score > 0 else 0

                st.markdown(f"###  {movie['title']}")
                st.progress(normalized_score)
                st.write(f" Skor: {round(score, 2)}")

    else:
        st.error("Hata oluştu!")