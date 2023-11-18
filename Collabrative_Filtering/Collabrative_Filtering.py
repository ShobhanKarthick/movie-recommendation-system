#!/usr/bin/env python
# coding: utf-8

# Collobrative Filtering

import pandas as pd


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


def get_similar_movies(movie, rating):
    """
    :movie: movie for which you want similar reccomendation
    :rating: rating of the movie
    """

    row = (sim_matrix[movie]*(rating - 2.5)).sort_values(ascending=False)
    return row


similar_movies = pd.DataFrame()
for movie, rating in ratings:
    similar_movies = pd.concat([similar_movies, get_similar_movies(movie, rating)])

similar_movies.sum().sort_values(ascending=False)
