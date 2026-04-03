from fastapi import FastAPI
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

user_movie_matrix = None
user_similarity_df = None
movies_df = None


app=FastAPI()


def get_recommendations(user_id):
    global user_movie_matrix, user_similarity_df, movies_df

    similar_users = user_similarity_df[user_id].sort_values(ascending=False)
    top_users = similar_users.iloc[1:11]

    top_users_movies = user_movie_matrix.loc[top_users.index]

    weighted_movies = top_users_movies.multiply(top_users, axis=0)
    movie_scores = weighted_movies.sum(axis=0)

    target_user_movies = user_movie_matrix.loc[user_id]
    movie_scores = movie_scores[target_user_movies == 0]

    recommended_movies = movie_scores.sort_values(ascending=False).head(5)

    recommended_movies = recommended_movies.reset_index()
    recommended_movies.columns = ['movieId', 'score']

    recommended_movies = recommended_movies.merge(movies_df, on='movieId', how='left')
    recommended_movies = recommended_movies.dropna(subset=['title'])

    return recommended_movies[['title', 'score']].to_dict(orient='records')


@app.on_event("startup")
def load_data():
    global user_movie_matrix, user_similarity_df, movies_df

    print("🚀 Model yükleniyor...")

    df = pd.read_csv(os.path.join(DATA_DIR, "ratings_small.csv"))

    user_movie_matrix = df.pivot_table(
        index='userId',
        columns='movieId',
        values='rating'
    ).fillna(0)

    user_similarity = cosine_similarity(user_movie_matrix)

    user_similarity_df = pd.DataFrame(
        user_similarity,
        index=user_movie_matrix.index,
        columns=user_movie_matrix.index
    )

    # Movies dataset
    movies_df = pd.read_csv(os.path.join(DATA_DIR, "movies_metadata.csv"), low_memory=False)
    movies_df = movies_df[['id', 'title']]
    movies_df.columns = ['movieId', 'title']
    movies_df['movieId'] = pd.to_numeric(movies_df['movieId'], errors='coerce')

    print("✅ Model hazır!")

@app.get("/")
def home():
    return{"message":"API çalışıyor"}

@app.get("/recommend")
def recommend(user_id: int):
    movies = get_recommendations(user_id)
    return {"recommendations": movies}