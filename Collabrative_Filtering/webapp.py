# app.py
import streamlit as st
import pandas as pd
import requests

# ##################################################################################
# Initial Configs
# ##################################################################################

st.set_page_config(page_title="Movie Recommendation App")

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {
        visibility: hidden;
    }
    .stEmotionCache {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ##################################################################################
# Functions of recommendations engine
# ##################################################################################

def standardize(row):
    new_row = (row - row.mean()) / (row.max() - row.min())
    return new_row


# Import data
movies = pd.read_csv("ml-latest-small/movies.csv")
ratings = pd.read_csv("ml-latest-small/ratings.csv")
df = movies.merge(ratings, left_on="movieId", right_on="movieId")

# Create a pivot table
user_ratings = df.pivot_table(index=['userId'], columns=['title'], values='rating')

# Drop movies with less than 10 user ratings
user_ratings = user_ratings.dropna(thresh=15, axis=1).fillna(0)

# Building the similarity matrix
sim_matrix = user_ratings.corr(method="pearson")


def get_similar_movies(sim_matrix, movie, rating):
    """
    :movie: movie for which you want similar reccomendation
    :rating: rating of the movie
    """

    row = (sim_matrix[movie]*(rating - 2.5)).sort_values(ascending=False)
    return row


def recommendation_handler(sim_matrix, selected_movies):
    similar_movies = pd.DataFrame()
    for movie in selected_movies:
        similar_movies = pd.concat([similar_movies, get_similar_movies(sim_matrix, movie, rating=5)], axis=1)

    # Return top 6 recommendations
    arr = similar_movies.sum(axis=1).sort_values(ascending=False).index.tolist()
    arr = arr[len(selected_movies):len(selected_movies)+6]

    # Save it to state
    st.session_state.reccos = arr


# ##################################################################################
# Streamlit UI
# ##################################################################################

# Initialise state
if "reccos" not in st.session_state:
    st.session_state.reccos = []

st.title("Movie Recommendation App")

selected_movies = st.multiselect("Pick your favourite movies",
                                 options=list(sim_matrix.columns),
                                 max_selections=5,
                                 placeholder="Choose upto 5 movies")


def get_poster(movie):
    """
    :movie: Movie for which poster should be retrived
    Retrives the entry form TMDB database and gets the poster path
    Returns the poster url if available else dummy poster path
    """
    movie = movie[:-7].replace(" ", "+").replace(")", "%29").replace("(", "%28")
    search_url = "https://api.themoviedb.org/3/search/movie?query={}&api_key=959fd8eac54614cd54dc3a06954f55cd".format(movie)
    data = requests.get(search_url)
    data = data.json()
    print(search_url)

    try:
        poster_path = data['results'][0]['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
    except Exception:
        full_path = "https://screench.com/upload/no-poster.jpeg"

    return full_path


if st.button("Recommend",
             use_container_width=True,
             on_click=recommendation_handler(sim_matrix, selected_movies)):

    col1, col2, col3 = st.columns(3)

    if len(st.session_state.reccos) > 0:
        movies = st.session_state.reccos
        with col1:
            st.write(movies[0])
            st.image(get_poster(movies[0]))

            st.write(movies[1])
            st.image(get_poster(movies[1]))

        with col2:
            st.write(movies[2])
            st.image(get_poster(movies[2]))

            st.write(movies[3])
            st.image(get_poster(movies[3]))

        with col3:
            st.write(movies[4])
            st.image(get_poster(movies[4]))

            st.write(movies[5])
            st.image(get_poster(movies[5]))
