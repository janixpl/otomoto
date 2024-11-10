import tensorflow as tf
import mlflow
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download('punkt_tab')

text_path = "data/syzyfowe-prace.txt"
try:
    with open(text_path, 'r', encoding='utf-8') as file:
        text = file.read()
except FileNotFoundError:
    print("Plik nie został znaleziony.")

sentences = sent_tokenize(text)

tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]

print("Sentences:", sentences)
print("Tokenized Sentences:", tokenized_sentences)