# import streamlit as st
# #import pandas as pd
# import pickle
# import numpy as np
# import requests
#
#
# movies = pickle.load(open('movie_list.pkl','rb'))
# similarity = pickle.load(open('similarity.pkl','rb'))
#
# df1 = movies
# similarity = np.array(similarity)
#
# api = '36f1b45e581b80df64c376a52b28e353'
# poster_path = 'https://image.tmdb.org/t/p/w500'
#
# def poster_fetch(movie_id):
#      response = requests.get(url = "https://api.themoviedb.org/3/movie/{}api_key=36f1b45e581b80df64c376a52b28e353&language=en-US".format(movie_id))
#      data = response.json()
#      return poster_path+data['poster_path']
#
#
# def recommend(movie):
#     index = df1[df1['title_x'] == movie].index[0]
#     distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
#     rec_list = []
#     movie_poster = []
#     for i in distances[1:11]:
#         rec_list.append( df1.iloc[i[0]].title_x)
#         movie_poster.append(poster_fetch(df1.iloc[i[0]].movie_id))
#     return movie_poster,rec_list
#
# st.title("Movie recommendation system!!!!")
#
# movie_selected = st.selectbox('Select a movie you watched',movies['title_x'].values)
#
# if st.button('Recommend'):
#     recommendation = recommend(movie_selected)
#     for i in recommendation:
#         st.write(i[1])
#
#
# ## ---------------

import streamlit as st
# pip import pickle
import numpy as np
import requests
import pandas as pd

df1 = pd.read_csv('df1.csv')

# movies = pickle.load(open('movie_list.pkl','rb'))
# similarity = pickle.load(open('similarity.pkl','rb'))
#
#
# df1 = movies

from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer(max_features=5000,stop_words='english')
vector = cv.fit_transform(df1['tag'])
from sklearn.metrics.pairwise import cosine_similarity
similarity = cosine_similarity(vector)


similarity = np.array(similarity)


api_key = '36f1b45e581b80df64c376a52b28e353'  # Store API key in a variable
poster_path = 'https://image.tmdb.org/t/p/w500'

def poster_fetch(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US" # f-string and correct URL
    try:
        response = requests.get(url)  # No need for extra headers
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if 'poster_path' in data and data['poster_path']: # Check if poster_path exists AND is not null/empty
            return poster_path + data['poster_path']
        else:
            return None  # Or a placeholder image URL
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for movie {movie_id}: {e}")
        return None  # Or a placeholder image URL
    except (KeyError, ValueError) as e: # Handle potential JSON decoding errors
        print(f"Error processing JSON response: {e}")
        return None

def recommend(movie):
    try:
        index = df1[df1['title_x'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        rec_list = []
        movie_posters = []  # Changed variable name for clarity
        for i in distances[1:11]:
            recommended_movie = df1.iloc[i[0]].title_x
            rec_list.append(recommended_movie)
            poster = poster_fetch(df1.iloc[i[0]].movie_id)
            movie_posters.append(poster)  # Store the poster URL (or None)
        return movie_posters, rec_list  # Return both lists
    except IndexError:
        st.warning(f"Movie '{movie}' not found in the dataset.")
        return [], []
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return [], []

st.title("Movie recommendation system!!!!")

movie_selected = st.selectbox('Select a movie you watched', movies['title_x'].values)

if st.button('Recommend'):
    movie_posters, recommendations = recommend(movie_selected)

    if recommendations:
        st.write("Recommended movies:")

        st.markdown(
            """
            <style>
            .grid-container {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                grid-gap: 5px;
            }
            .grid-item {
                text-align: center;
            }
            .movie-title { /* Style for movie titles */
                font-weight: bold;
                font-size: 16px; /* Adjust size as needed */
                margin-bottom: 5px; /* Space between title and poster */
            }
            .poster-not-available { /* Style for "Poster not available" */
                font-style: italic;
                color: red;
                font-size: 12px; /* Adjust size as needed */
                margin-top: 5px; /* Space from poster if no poster*/
            }
            .grid-item img {
                max-width: 200px;
                max-height: 250px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.write("<div class='grid-container'>", unsafe_allow_html=True)

        for i in range(len(recommendations)):
            row = i // 5
            col = i % 5

            if i % 5 == 0:
                cols = st.columns(5)

            with cols[col]:
                st.markdown(f"<div class='grid-item'><span class='movie-title'>{recommendations[i]}</span><br>",
                            unsafe_allow_html=True)  # Movie Name with class
                if movie_posters[i]:
                    st.image(movie_posters[i])
                else:
                    st.markdown("<span class='poster-not-available'>Poster not available.</span>",
                                unsafe_allow_html=True)  # Styled message
                st.write("</div>", unsafe_allow_html=True)

        st.write("</div>", unsafe_allow_html=True)