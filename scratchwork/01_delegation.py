import spacy
import pandas as pd

# Load the text file
with open("data/PL094_240.txt", "r") as file:
    text = file.read()

# Split the text into sections based on typical section headers
sections = text.split('SEC.')

# Create a DataFrame with the sections data
data = []
for i, section in enumerate(sections):
    if section.strip():  # Ensure the section is not empty
        section_name = f"Section {i}"
        citation = "Public Law 94-240"
        section_id = i
        data.append({'name': section_name, 'citation': citation, 'id': section_id, 'text': section.strip()})

df = pd.DataFrame(data)

# Load NLP
nlp = spacy.load("myenv/lib/python3.12/site-packages/en_core_web_sm/en_core_web_sm-3.7.1")

# List the modals and verbs
strict_modals = ['shall', 'must', 'will']
permissive_modals = ['may', 'can']
other_modals = ['should', 'would', 'could', 'might']
obligation_verbs = ['require', 'expect', 'compel', 'oblige', 'obligate', 'have to', 'ought to']
constraint_verbs = ['prohibit', 'forbid', 'ban', 'bar', 'restrict', 'proscribe']
permission_verbs = ['allow', 'permit', 'authorize']
entitlement_verbs = ['have', 'receive', 'retain']
special_verbs = obligation_verbs + constraint_verbs + permission_verbs + entitlement_verbs

# Define the functions as before
def permission(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
               permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs, entitlement_verbs):
    way1 = any(set(permission_verbs).intersection(lemma_dict.keys())) and "neg" not in dep_dict
    way2 = any(set(permissive_modals).intersection(lemma_dict.keys())) and "VERB" in speech_dict.keys() and not any(
        set(special_verbs).intersection(lemma_dict.keys())) and "neg" not in dep_dict
    way3 = "neg" in dep_dict and any(set(constraint_verbs).intersection(lemma_dict.keys()))
    anyTrue = way1 or way2 or way3
    return 1 if anyTrue else 0

def obligation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
               permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs, entitlement_verbs):
    if "neg" in dep_dict:
        return 0
    way1 = any(set(strict_modals).intersection(lemma_dict.keys())) and 'be' not in lemma_dict
    way2 = any(set(strict_modals).intersection(lemma_dict.keys())) and any(
        set(obligation_verbs).intersection(lemma_dict.keys()))
    way3 = 'MD' not in tokentg_dict and any(set(obligation_verbs).intersection(lemma_dict.keys()))
    anyTrue = way1 or way2 or way3
    return 1 if anyTrue else 0

def constraint(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
               permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs, entitlement_verbs):
    way1 = "neg" in dep_dict and 'MD' in tokentg_dict and not any(set(obligation_verbs).intersection(lemma_dict.keys()))
    way2 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and any(
        set(constraint_verbs).intersection(lemma_dict.keys()))
    way3 = "neg" in dep_dict and any(set(permission_verbs).intersection(lemma_dict.keys()))
    anyTrue = way1 or way2 or way3
    return 1 if anyTrue else 0

def entitlement(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,entitlement_verbs):
    way1 = "neg" not in dep_dict and any(set(entitlement_verbs).intersection(lemma_dict.keys()))
    way2 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and 'be' in lemma_dict
    way3 = "neg" in dep_dict and any(set(obligation_verbs).intersection(lemma_dict.keys()))
    anyTrue = way1 or way2 or way3
    return 1 if anyTrue else 0

def mandatory_delegation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,entitlement_verbs):
    way1 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys()))
    anyTrue = way1
    return 1 if anyTrue else 0

def permissive_delegation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,entitlement_verbs):
    way1 = "neg" not in dep_dict and any(set(permissive_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))
    anyTrue = way1
    return 1 if anyTrue else 0

def permissive_provision(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,entitlement_verbs):
    way1 = "neg" not in dep_dict and any(set(permissive_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))
    anyTrue = way1
    return 1 if anyTrue else 0

def mandatory_provision(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,entitlement_verbs):
    way1 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))
    anyTrue = way1
    return 1 if anyTrue else 0

def constraining_provision(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,entitlement_verbs):
    way1 = "neg" in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))
    anyTrue = way1
    return 1 if anyTrue else 0

cols = ['name','citation','id','obligation', 'constraint','permission','entitlement','MandatoryDelegation',
        'Permissive Delegation', 'PermissiveProvision','MandatoryProvision', 'Constraining Provision']

# Tokenize the text
docs = list(nlp.pipe(df.text))
provisions_lst = []

for index, provision in enumerate(docs):
    # This is the provision level where we want to aggregate the OCPE tagging
    obligation_lst = []
    constraint_lst = []
    permission_lst = []
    entitlement_lst = []
    mand_del_lst = []
    perm_del_lst = []
    perm_prov_lst = []
    mand_prov_lst = []
    const_prov_lst = []

    for sentence in provision.sents:
        dep_dict = {}
        tokentg_dict = {}
        lemma_dict = {}
        token_dict = {}
        speech_dict = {}

        for token in sentence:
            dep_dict[token.dep_] = token.text
            tokentg_dict[token.tag_] = token.text
            lemma_dict[token.lemma_] = token.text
            speech_dict[token.pos_] = token.text

        permis = permission(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                            permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,
                            entitlement_verbs)
        obl = obligation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                          permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,
                          entitlement_verbs)
        const = constraint(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                           permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,
                           entitlement_verbs)
        entitle = entitlement(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                              permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,
                              entitlement_verbs)
        #Nir Kosti additions
        mand_del = mandatory_delegation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                              permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,
                              entitlement_verbs)
        perm_del = permissive_delegation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                              permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,
                              entitlement_verbs)
        perm_prov = permissive_provision(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                              permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,
                              entitlement_verbs)
        mand_prov = mandatory_provision(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                              permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,
                              entitlement_verbs)
        const_prov = constraining_provision(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                              permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs,
                              entitlement_verbs)

        obligation_lst.append(obl)
        constraint_lst.append(const)
        permission_lst.append(permis)
        entitlement_lst.append(entitle)
        # Nir add-ons
        mand_del_lst.append(mand_del)
        perm_del_lst.append(perm_del)
        perm_prov_lst.append(perm_prov)
        mand_prov_lst.append(mand_prov)
        const_prov_lst.append(const_prov)

    provisions_lst.append(
            [df["name"].iloc[index], df["citation"].iloc[index],df["id"].iloc[index],sum(obligation_lst), sum(constraint_lst),
             sum(permission_lst),
             sum(entitlement_lst),
             sum(mand_del_lst),
             sum(perm_del_lst),
             sum(perm_prov_lst),
             sum(mand_prov_lst),
             sum(const_prov_lst)
             ])

df1 = pd.DataFrame(provisions_lst, columns=cols)

df1.to_csv("PL094_240_provisions.csv")
