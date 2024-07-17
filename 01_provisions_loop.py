import spacy
import pandas as pd
import re
import os
import glob
import argparse

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('-filepath', '-f', type=str, help='Put the path here')
parser.add_argument('-ending', '-e', type=str, help='End of filepath for CSV')
args = parser.parse_args()

# Default path and ending
path = args.filepath if args.filepath else 'data/too_long'
end1 = args.ending if args.ending else '-FR'

print("Path:", path)
print("Ending:", end1)

# Function to separate preamble
def separate_preamble(doc):
    doc = doc.lower()
    
    # Try to find the start of the main content based on typical patterns in Public Laws
    start_patterns = ['public law', 'section 1', 'be it enacted', 'an act', 'section 101']
    start_pos = None
    
    for pattern in start_patterns:
        match = re.search(pattern, doc)
        if match:
            start_pos = match.start()
            break

    if start_pos is None:
        print("No way to parse rule text, go onto the next iteration")
        print("Document content (first 500 characters):")
        print(doc[:500])
        return ""

    return doc[start_pos:]

# Function to find all occurrences of a substring (unchanged)
def find_all(text, substring):
    return [i for i in range(len(text)) if text.startswith(substring, i)]

# Function to split text into chunks
def split_text_into_chunks(text, chunk_size=10000):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield ' '.join(words[i:i + chunk_size])

# Load spaCy model
nlp = spacy.load('myenv/lib/python3.12/site-packages/en_core_web_sm/en_core_web_sm-3.7.1')  # Ensure this model is installed

# Define modal and verb lists
strict_modals = ['shall', 'must', 'will']
permissive_modals = ['may', 'can']
other_modals = ['should', 'would', 'could', 'might']
obligation_verbs = ['require', 'expect', 'compel', 'oblige', 'obligate', 'have to', 'ought to']
constraint_verbs = ['prohibit', 'forbid', 'ban', 'bar', 'restrict', 'proscribe']
permission_verbs = ['allow', 'permit', 'authorize']
entitlement_verbs = ['have', 'receive', 'retain']
special_verbs = obligation_verbs + constraint_verbs + permission_verbs + entitlement_verbs

# Functions to check provision types
def obligation(dep_dict, lemma_dict, tokentg_dict, special_verbs, strict_modals, obligation_verbs):
    if "neg" in dep_dict:
        return 0
    way1 = any(set(strict_modals).intersection(lemma_dict.keys())) and 'be' not in lemma_dict
    way2 = any(set(strict_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))
    way3 = 'MD' not in tokentg_dict and any(set(obligation_verbs).intersection(lemma_dict.keys()))
    return 1 if way1 or way2 or way3 else 0

def constraint(dep_dict, lemma_dict, tokentg_dict, strict_modals, constraint_verbs, permission_verbs):
    way1 = "neg" in dep_dict and 'MD' in tokentg_dict and not any(set(obligation_verbs).intersection(lemma_dict.keys()))
    way2 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and any(set(constraint_verbs).intersection(lemma_dict.keys()))
    way3 = "neg" in dep_dict and any(set(permission_verbs).intersection(lemma_dict.keys()))
    return 1 if way1 or way2 or way3 else 0

def permission(dep_dict, lemma_dict, permissive_modals, constraint_verbs, special_verbs):
    way1 = "neg" not in dep_dict and any(set(permission_verbs).intersection(lemma_dict.keys()))
    way2 = "neg" not in dep_dict and any(set(permissive_modals).intersection(lemma_dict.keys())) and not any(set(special_verbs).intersection(lemma_dict.keys()))
    way3 = "neg" in dep_dict and any(set(constraint_verbs).intersection(lemma_dict.keys()))
    return 1 if way1 or way2 or way3 else 0

def entitlement(dep_dict, lemma_dict, tokentg_dict, strict_modals, entitlement_verbs):
    way1 = "neg" not in dep_dict and any(set(entitlement_verbs).intersection(lemma_dict.keys()))
    way2 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and 'be' in lemma_dict
    way3 = "neg" in dep_dict and any(set(obligation_verbs).intersection(lemma_dict.keys()))
    return 1 if way1 or way2 or way3 else 0

# Columns for DataFrame
cols = ['law_name', 'length', 'obligation', 'constraint', 'permission', 'entitlement', 'agency_obligation', 'agency_constraint', 'agency_permission', 'agency_entitlement', 'entity_obligation', 'entity_constraint', 'entity_permission', 'entity_entitlement']
provisions_lst = []

# Get list of files
rules = glob.glob(os.path.join(path, "*.txt"))

for rl in rules:
    print("Processing file:", rl)
    
    with open(rl, 'r', encoding='utf8') as file:
        doc = file.read()

    preamble = separate_preamble(doc)
    if not preamble:
        print(f"Failed to parse document: {rl}")
        continue
    
    # Extract the law name from the filename
    law_name = os.path.splitext(os.path.basename(rl))[0]

    doc_length = 0
    total_obligation = 0
    total_constraint = 0
    total_permission = 0
    total_entitlement = 0
    total_agency_obligation = 0
    total_agency_constraint = 0
    total_agency_permission = 0
    total_agency_entitlement = 0
    total_entity_obligation = 0
    total_entity_constraint = 0
    total_entity_permission = 0
    total_entity_entitlement = 0

    for chunk in split_text_into_chunks(preamble):
        doc_spacy = nlp(chunk)
        doc_length += len(chunk.split())

        for sent in doc_spacy.sents:
            dep_dict = {token.dep_: token.i for token in sent}
            tokentg_dict = {token.tag_: token.i for token in sent}
            lemma_dict = {token.lemma_: token.i for token in sent}
            token_dict = {token.text: token.i for token in sent}
            speech_dict = {token.pos_: token.i for token in sent}

            obl = obligation(dep_dict, lemma_dict, tokentg_dict, special_verbs, strict_modals, obligation_verbs)
            const = constraint(dep_dict, lemma_dict, tokentg_dict, strict_modals, constraint_verbs, permission_verbs)
            permis = permission(dep_dict, lemma_dict, permissive_modals, constraint_verbs, special_verbs)
            entitle = entitlement(dep_dict, lemma_dict, tokentg_dict, strict_modals, entitlement_verbs)

            total_obligation += obl
            total_constraint += const
            total_permission += permis
            total_entitlement += entitle

            if obl == 0 and const == 0 and permis == 0 and entitle == 0:
                continue

            for chunk in sent.noun_chunks:
                if chunk.root.dep_ == "nsubj":
                    if bool(re.search('agency|commission|board|agencies', chunk.lemma_)) or bool(re.search('[A-Z]{3,}', chunk.text)):
                        if obl == 1:
                            total_agency_obligation += 1
                        if const == 1:
                            total_agency_constraint += 1
                        if permis == 1:
                            total_agency_permission += 1
                        if entitle == 1:
                            total_agency_entitlement += 1
                    else:
                        if obl == 1:
                            total_entity_obligation += 1
                        if const == 1:
                            total_entity_constraint += 1
                        if permis == 1:
                            total_entity_permission += 1
                        if entitle == 1:
                            total_entity_entitlement += 1

    provisions_lst.append([
        law_name, doc_length,
        total_obligation, total_constraint, total_permission, total_entitlement, 
        total_agency_obligation, total_agency_constraint, total_agency_permission, total_agency_entitlement, 
        total_entity_obligation, total_entity_constraint, total_entity_permission, total_entity_entitlement
    ])

# Convert the list of provisions to a DataFrame and save as CSV
df1 = pd.DataFrame(provisions_lst, columns=cols)
nms = "DF-Rules" + end1 + ".csv"
df1.to_csv(nms, index=False)

print("DataFrame saved to:", nms)
print(df1)
