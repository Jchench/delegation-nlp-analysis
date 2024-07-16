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
path = args.filepath if args.filepath else 'data/test/'

print("Path:", path)

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

# Load spaCy model
nlp = spacy.load('myenv/lib/python3.12/site-packages/en_core_web_sm/en_core_web_sm-3.7.1')

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
    
    doc_length = len(preamble.split())
    if doc_length > 300000:
        print("Document too long and coder too lazy to loop over portions of document")
        continue

    doc_spacy = nlp(preamble)  # Ensure preamble is processed by spaCy
    obligation_lst = []
    constraint_lst = []
    permission_lst = []
    entitlement_lst = []
    agency_obligation_lst = []
    agency_constraint_lst = []
    agency_permission_lst = []
    agency_entitlement_lst = []
    entity_obligation_lst = []
    entity_constraint_lst = []
    entity_permission_lst = []
    entity_entitlement_lst = []

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

        obligation_lst.append(obl)
        constraint_lst.append(const)
        permission_lst.append(permis)
        entitlement_lst.append(entitle)

        if obl == 0 and const == 0 and permis == 0 and entitle == 0:
            continue

        for chunk in sent.noun_chunks:
            if chunk.root.dep_ == "nsubj":
                if bool(re.search('agency|commission|board|agencies', chunk.lemma_)) or bool(re.search('[A-Z]{3,}', chunk.text)):
                    if obl == 1:
                        agency_obligation_lst.append(1)
                    if const == 1:
                        agency_constraint_lst.append(1)
                    if permis == 1:
                        agency_permission_lst.append(1)
                    if entitle == 1:
                        agency_entitlement_lst.append(1)
                else:
                    if obl == 1:
                        entity_obligation_lst.append(1)
                    if const == 1:
                        entity_constraint_lst.append(1)
                    if permis == 1:
                        entity_permission_lst.append(1)
                    if entitle == 1:
                        entity_entitlement_lst.append(1)

    # Extract the law name using a regular expression
    law_name_match = re.search(r'public law \d+-\d+', preamble, re.IGNORECASE)
    law_name = law_name_match.group() if law_name_match else "N/A"

    provisions_lst.append([
        law_name, doc_length, 
        sum(obligation_lst), sum(constraint_lst), sum(permission_lst), sum(entitlement_lst), 
        sum(agency_obligation_lst), sum(agency_constraint_lst), sum(agency_permission_lst), sum(agency_entitlement_lst), 
        sum(entity_obligation_lst), sum(entity_constraint_lst), sum(entity_permission_lst), sum(entity_entitlement_lst)
    ])

# Convert the list of provisions to a DataFrame and save as CSV
df1 = pd.DataFrame(provisions_lst, columns=cols)
nms = "Public_laws" + ".csv"
df1.to_csv(nms, index=False)

print("DataFrame saved to:", nms)
print(df1)
