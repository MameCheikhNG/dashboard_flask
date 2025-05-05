import os
import sys

# Définir l'exécutable Python (ajuste si nécessaire)
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


from pyspark import SparkContext

# Initialisation du SparkContext
sc = SparkContext()

# Lecture du fichier texte en un RDD de lignes
lines = sc.textFile("text.txt")

# Traitement des lignes pour obtenir les mots et les compter
word_counts = (lines
               # Découpe chaque ligne en mots
               .flatMap(lambda line: line.split(' '))
               # Nettoie les mots en les convertissant en minuscules et en supprimant la ponctuation
               .map(lambda word: word.lower().strip(",.!?"))
               # Crée une paire (mot, 1) pour chaque mot
               .map(lambda word: (word, 1))
               # Réduit par clé (mot), additionne les valeurs associées à chaque mot
               .reduceByKey(lambda count1, count2: count1 + count2)
               # Collecte les résultats sous forme de liste
               .collect())

# Affichage des résultats
for word, count in word_counts:
    print(f"{word}: {count}")
