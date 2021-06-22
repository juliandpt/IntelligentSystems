import pandas as pd
import sqlite3
import numpy as np
from math import sqrt

con = sqlite3.connect('./RecomendationSystem/database/database.db')
cur = con.cursor()

ratings = pd.read_sql("SELECT * FROM Ratings;", con)
movies = pd.read_sql("SELECT * FROM Movies;", con)

def recomendation(usu, num_vecinos, grado_similitud, num_peliculas):
    #obtener las peliculas de ese usuario
    inputid = ratings.loc[ratings['userId'] == usu]
    inputMovies = pd.merge(inputid, movies)
    inputMovies = inputMovies.drop(['timestamp','genres','userId'], 1)

    #obtener los usuarios que han visto las mismas películas
    userSubset = ratings[ratings['movieId'].isin(inputMovies['movieId'].tolist())].drop('timestamp',1)

    #eliminamos del df al usuario escogido
    userSubset = userSubset.loc[userSubset['userId'] != usu]

    #agrupamos las filas por el idusuario
    userSubsetGroup = userSubset.groupby(['userId'])

    #ordenamos los usuarios para que los que compartan la mayor cantidad de películas tengan prioridad
    userSubsetGroup = sorted(userSubsetGroup, key=lambda x: len(x[1]), reverse=True)

    #pasamos por el número de vecinos que hemos puesto en parámetro
    userSubsetGroup = userSubsetGroup[0:num_vecinos]

    #calculamos la correlación de Pearson
    pearsonCorrelationDict = {}
    for name, group in userSubsetGroup:
        group = group.sort_values(by='movieId')
        inputMovies = inputMovies.sort_values(by='movieId')

        #se obtiene el tamano de ese grupo para hacer la media mas tarde
        nRatings = len(group)
        
        #Obtener los puntajes de revisión para las películas en común con los vecinos
        temp_df = inputMovies[inputMovies['movieId'].isin(group['movieId'].tolist())]

        #Guardarlas en una variable temporal con formato de lista para facilitar cálculos futuros
        tempRatingList = temp_df['rating'].tolist()

        #Pongamos también las revisiones de grupos de usuarios en una lista
        tempGroupList = group['rating'].tolist()
        
        #Calculemos la Correlación Pearson entre dos usuarios, x e y
        Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
        Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
        Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)

        #Si el denominador es diferente a cero, entonces dividir, sino, la correlación es 0.
        if Sxx != 0 and Syy != 0:
            pearsonCorrelationDict[name] = Sxy/sqrt(Sxx*Syy)
        else:
            pearsonCorrelationDict[name] = 0
    #aqui construimos la matriz con el id del vecino y el grado de similitud que tiene con el usuario original
    pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
    pearsonDF.columns = ['similarityIndex']
    pearsonDF['userId'] = pearsonDF.index
    pearsonDF.index = range(len(pearsonDF))
    #obtenemos los que tengan el grado de similitud mayor parametro
    pearsonDF = pearsonDF.loc[pearsonDF['similarityIndex'] >= grado_similitud]

    #Obtenemos los primeros 50 registros (el limite es 50)
    topUsers=pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:50]

    #buscamos las peliculas de esos usuarios
    topUsersRating=topUsers.merge(ratings, left_on='userId', right_on='userId', how='inner')
    topUsersRating = topUsersRating.drop('timestamp', 1)

    #multiplicar puntuacion de la película por su peso (El índice de similitud), luego se suman los nuevos puntajes y dividen por la suma de los pesos.
    topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['rating']

    #Se aplica una suma a los topUsers luego de agruparlos por userId
    tempTopUsersRating = topUsersRating.groupby('movieId').sum()[['similarityIndex','weightedRating']]
    tempTopUsersRating.columns = ['sum_similarityIndex','sum_weightedRating']

    #Se crea un dataframe vacío
    recommendation_df = pd.DataFrame()

    #Ahora se toma el promedio ponderado
    recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
    recommendation_df['movieId'] = tempTopUsersRating.index

    #ordenamos
    recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)
    return movies.loc[movies['movieId'].isin(recommendation_df.head(num_peliculas)['movieId'].tolist())]['title']

def punctuation(usu, movie):
    #obtener las peliculas de ese usuario
    inputid = ratings.loc[ratings['userId'] == usu]
    inputMovies = pd.merge(inputid,movies)
    inputMovies = inputMovies.drop(['timestamp','genres','userId'],1)

    #obtener los usuarios que han visto las mismas películas
    userSubset = ratings[ratings['movieId'].isin(inputMovies['movieId'].tolist())].drop('timestamp',1)
    #eliminamos del df al usuario escogido
    userSubset = userSubset.loc[userSubset['userId'] != usu]

    #agrupamos las filas por el idusuario
    userSubsetGroup = userSubset.groupby(['userId'])

    #ordenamos los usuarios para que los que compartan la mayor cantidad de películas tengan prioridad
    userSubsetGroup = sorted(userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)

    #calculamos la correlación de Pearson
    pearsonCorrelationDict = {}
    for name, group in userSubsetGroup:
        group = group.sort_values(by='movieId')
        inputMovies = inputMovies.sort_values(by='movieId')

        #Obtener el N para la fórmula
        nRatings = len(group)
        
        #Obtener los puntajes de revisión para las películas en común
        temp_df = inputMovies[inputMovies['movieId'].isin(group['movieId'].tolist())]

        #Guardarlas en una variable temporal con formato de lista para facilitar cálculos futuros
        tempRatingList = temp_df['rating'].tolist()

        #Pongamos también las revisiones de grupos de usuarios en una lista
        tempGroupList = group['rating'].tolist()
        
        #Calculemos la Correlación Pearson entre dos usuarios, x e y
        Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
        Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
        Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)

        #Si el denominador es diferente a cero, entonces dividir, sino, la correlación es 0.
        if Sxx != 0 and Syy != 0:
            pearsonCorrelationDict[name] = Sxy/sqrt(Sxx*Syy)
        else:
            pearsonCorrelationDict[name] = 0

    pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
    pearsonDF.columns = ['similarityIndex']
    pearsonDF['userId'] = pearsonDF.index
    pearsonDF.index = range(len(pearsonDF))

    #buscamos las peliculas de esos usuarios
    topUsersRating=pearsonDF.merge(ratings, left_on='userId', right_on='userId', how='inner')
    topUsersRating = topUsersRating.drop('timestamp',1)

    #multiplicar puntuacion de la película por su peso (El índice de similitud), luego se suman los nuevos puntajes y dividen por la suma de los pesos.
    topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['rating']

    #Se aplica una suma a los topUsers luego de agruparlos por userId
    topUsersRating = topUsersRating.loc[topUsersRating['movieId'] == movie].groupby('movieId').sum()[['similarityIndex','weightedRating']]
    return topUsersRating['weightedRating'] / topUsersRating['similarityIndex']

def main():
    recomendation(6, 50, 0.3, 7)

if __name__ == "__main__":
    main()