import spacy

nlp = spacy.load("myenv/lib/python3.12/site-packages/en_core_web_sm/en_core_web_sm-3.7.1")

doc = nlp("This is a test sentence.")
for token in doc:
    print(token.text, token.pos_, token.dep_)
