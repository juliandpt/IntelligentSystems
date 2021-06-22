import tkinter
from tkinter import ttk
import sqlite3
from tkinter.constants import END, RIGHT
import RecomendationSystem

con = sqlite3.connect('./RecomendationSystem/database/database.db')
cur = con.cursor()

ventana = tkinter.Tk()
ventana.configure(background='#ECECEC')
ventana.title('Practica 2')
width = ventana.winfo_screenwidth() 
height = ventana.winfo_screenheight()
ventana.geometry("%dx%d" % (width, height))

header = tkinter.Label(ventana, text="Recomendaciones", font="Verdana 20 underline")
header.grid(row=0, column=2)

# PRIMERA PARTE

def getInput():
    displayText.delete(1.0, END)
    selectUser = comboUser.get()
    selectNeighbours = nNeighbours.get()
    selectItems = nItems.get()
    selectUmbral = nUmbral.get()
    result = RecomendationSystem.recomendation(int(selectUser), int(selectNeighbours), float(selectUmbral), int(selectItems))
    if result.empty:
        result = 'No hay resultados \n'
        displayText.configure(state='normal')
        displayText.insert(END, result)
        displayText.configure(state='disabled')
    else:
        displayText.configure(state='normal')
        displayText.insert(END, result)
        displayText.configure(state='disabled')

select = tkinter.Label(ventana, text="Selecciona un usuario", font="Verdana 15")
select.grid(row=1, column=0)

users = []
for row in cur.execute('SELECT DISTINCT userId FROM ratings'):
    users.append(row)

comboUser = ttk.Combobox(ventana, values=users, width = 10)
comboUser.grid(row=1, column=1)

neighbours = tkinter.Label(ventana, text="Numero de vecinos", font="Verdana 15")
neighbours.grid(row=1, column=2)

nNeighbours = tkinter.Entry(ventana, width = 5)
nNeighbours.grid(row=1, column=3)

items = tkinter.Label(ventana, text="Items del ranking", font="Verdana 15")
items.grid(row=2, column=0)

nItems = tkinter.Entry(ventana, width = 5)
nItems.grid(row=2, column=1)

umbral = tkinter.Label(ventana, text="Umbral del similitud", font="Verdana 15")
umbral.grid(row=2, column=2)

nUmbral = tkinter.Entry(ventana, width = 5)
nUmbral.grid(row=2, column=3)

recommend = tkinter.Button(ventana, text="¡Recomendar!", command = getInput)
recommend.grid(row=2, column=4)

ranking = tkinter.Label(ventana, text="Ranking:", font="Verdana 15")
ranking.grid(row=3, column=2)

displayText = tkinter.Text(ventana, height=20, width=60)
displayText.grid(row=4, column=2)
scroll = tkinter.Scrollbar(ventana, command=displayText.yview)

# SEGUNDA PARTE

def getInput2():
    selectUser2 = comboUser2.get()
    selectMovie = comboMovie.get().split('-')[0].split('{')[1]
    result = RecomendationSystem.punctuation(int(selectUser2), int(selectMovie))
    result = result.values
    displayText2.configure(state='normal')
    displayText2.insert(END, result)
    displayText2.configure(state='disabled')

def getMovies(user):
    movies = []
    for row in cur.execute("SELECT movieId || '-' || title AS peli FROM movies WHERE movieId not in (SELECT movieId FROM Ratings WHERE userId=" + user + ")"):
        movies.append(row)

    comboMovie["values"] = movies

select = tkinter.Label(ventana, text="Selecciona un usuario", font="Verdana 15")
select.grid(row=5, column=0)

users = []
for row in cur.execute('SELECT DISTINCT userId FROM ratings'):
        users.append(row)

comboUser2 = ttk.Combobox(ventana, values=users, width = 10)
comboUser2.grid(row=5, column=1)

def callback(eventObject):
    getMovies(comboUser2.get())

comboUser2.bind("<<ComboboxSelected>>", callback)

select = tkinter.Label(ventana, text="Selecciona una película", font="Verdana 15")
select.grid(row=6, column=0)

comboMovie = ttk.Combobox(ventana, width = 30)
comboMovie.grid(row=6, column=1)

predictButton = tkinter.Button(ventana, text="¡Predecir!", command = getInput2)
predictButton.grid(row=6, column=2)

predict = tkinter.Label(ventana, text="Predicción: ", font="Verdana 15")
predict.grid(row=7, column=0)

displayText2 = tkinter.Text(ventana, height=20, width=60)
displayText2.grid(row=8, column=2)
scroll = tkinter.Scrollbar(ventana, command=displayText2.yview)

ventana.mainloop()