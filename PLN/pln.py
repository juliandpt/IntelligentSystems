import nltk, xlrd, string
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

def readExcel(path):
    texts = []
    archive = xlrd.open_workbook(path)
    document = archive.sheet_by_index(0)

    for i in range (1, document.nrows):
        texts.append(document.cell_value(i, 7))

    return texts

def cleanText(texts):
    cleanedTexts = []

    for text in texts:
        eliminateItems = string.punctuation + "1234567890•‘" 
        cleanedTexts.append(text.translate(str.maketrans('', '', eliminateItems)).replace('\n', ''))

    cleanedTexts = list(map(lambda texto: texto.lower(), cleanedTexts))

    return cleanedTexts

def textProcess(texts):
    textsAux = []
    sw = set(stopwords.words('spanish'))
    ps = PorterStemmer()

    textsAux = [nltk.word_tokenize(i) for i in texts]

    for i in range(len(textsAux)): 
        tokenizedTexts = []
        for w in range(len(textsAux[i])): 
            if textsAux[i][w] not in sw:  
                tokenizedTexts.append(textsAux[i][w])
        textsAux[i] = tokenizedTexts

    for i in range(len(textsAux)): 
        stemizedTexts = []
        for w in range(len(textsAux[i])):
            stemizedTexts.append(ps.stem(textsAux[i][w]))
        textsAux[i] = stemizedTexts

    return textsAux

def vectorize(query, texts):
    sw = set(stopwords.words('spanish'))
    vectorizer = TfidfVectorizer(stop_words = sw)
    vectors = []

    query = vectorizer.fit_transform([str(query)])

    for i in range(len(texts)): 
        vectors.append(vectorizer.transform([str(texts[i])]))

    return query, vectors

def distanceCalculation(vectorizedQuery, vectorizedTexts):
    distances = []

    for i in range(len(vectorizedTexts)):
        distances.append(cosine_similarity(vectorizedQuery, vectorizedTexts[i])[0][0])

    return distances

def sentiments(distances, texts):
    rankings = dict()
    rankings['cosines'] = []
    rankings['textSentiments'] = []

    for i in range(len(distances)):
        if len(rankings['cosines']) < 5:
            rankings['cosines'].append(distances[i])
            rankings['textSentiments'].append(texts[i])
        else:
            for j in range(len(rankings['cosines'])):
                if rankings['cosines'][j] < distances[i]:
                    rankings['cosines'][j] = distances[i]
                    rankings['textSentiments'][j] = texts[i]

    for i in range(len(rankings['textSentiments'])):
        rankings['textSentiments'][i] = ('Text: {}, polarity: {}, subjetivity: {}'.format(rankings['textSentiments'][j], TextBlob(rankings['textSentiments'][j]).sentiment.polarity, TextBlob(rankings['textSentiments'][j]).sentiment.subjectivity))

    return rankings

def main():
    path = "PLN/data/tweets.xls"
    texts = dict()

    texts['documents'] = readExcel(path)
    texts['documents'] = cleanText(texts['documents'])
    texts['query'] = input('Introduzca la query deseada: ')
    texts['query'], texts['vectors'] = vectorize(texts['query'], texts['documents'])
    texts['distances'] = distanceCalculation(texts['query'], texts['vectors'])
    texts['rankings'] = sentiments(texts['distances'], texts['documents'])

    print(texts['rankings'])

main()