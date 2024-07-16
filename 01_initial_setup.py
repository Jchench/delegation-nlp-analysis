import spacy
import pandas as pd

nlp = spacy.load("myenv/lib/python3.12/site-packages/en_core_web_sm/en_core_web_sm-3.7.1")

with open("data/PL094_240.txt", "r") as f:
  text = f.read()

doc = nlp(text)

for sent in doc.sents:
  print (sent)
