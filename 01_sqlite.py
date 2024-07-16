import spacy
import pandas as pd
import sqlite3

# see https://web.archive.org/web/20201106053441id_/http://dlc.dlib.indiana.edu/dlc/bitstream/handle/10535/10485/VannoniAshMorelli_2019.pdf?sequence=1&isAllowed=y

# Create a SQL connection to our SQLite database
con = sqlite3.connect("/Users/stevenrashin/Dropbox/Threatening Rules/Threatening Rules/Data/df_text.sqlite")
cur = con.cursor()
df = pd.read_sql_query("SELECT * from textdata", con)

# Verify that result of SQL query is stored in the dataframe
print(df.head())

# Be sure to close the connection
con.close()

# Load NLP
nlp = spacy.load('en_core_web_lg')

# List the modals
strict_modals = ['shall', 'must', 'will']
permissive_modals = ['may', 'can']
other_modals = ['should', 'would', 'could', 'might']
obligation_verbs = ['require', 'expect', 'compel', 'oblige', 'obligate', 'have to', 'ought to']
constraint_verbs = ['prohibit', 'forbid', 'ban', 'bar', 'restrict', 'proscribe']
permission_verbs = ['allow', 'permit', 'authorize']
entitlement_verbs = ['have', 'receive', 'retain']
special_verbs = obligation_verbs + constraint_verbs + permission_verbs + entitlement_verbs

# create all the functions
# for the functions all have the same input (even the unused args) to make calling function easier
def permission(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
               permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs, entitlement_verbs):

    way1 = any(set(permission_verbs).intersection(lemma_dict.keys())) and "neg" not in dep_dict
    way2 = any(set(permissive_modals).intersection(lemma_dict.keys())) and "VERB" in speech_dict.keys() and not any(
        set(special_verbs).intersection(lemma_dict.keys())) and "neg" not in dep_dict
    way3 = "neg" in dep_dict and any(set(constraint_verbs).intersection(lemma_dict.keys()))

    anyTrue = way1 or way2 or way3

    if anyTrue == True:
        return 1
    else:
        return 0


def obligation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
               permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs, entitlement_verbs):

    if "neg" in dep_dict:
        return 0
    else:
        way1 = any(set(strict_modals).intersection(lemma_dict.keys())) and 'be' not in lemma_dict
        way2 = any(set(strict_modals).intersection(lemma_dict.keys())) and any(
            set(obligation_verbs).intersection(lemma_dict.keys()))
        way3 = 'MD' not in tokentg_dict and any(set(obligation_verbs).intersection(lemma_dict.keys()))
        anyTrue = way1 or way2 or way3
        if anyTrue == True:
            return 1
        else:
            return 0


def constraint(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
               permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs, entitlement_verbs):
                 
    way1 = "neg" in dep_dict and 'MD' in tokentg_dict and not any(set(obligation_verbs).intersection(lemma_dict.keys()))
    way2 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and any(
        set(constraint_verbs).intersection(lemma_dict.keys()))
    way3 = "neg" in dep_dict and any(set(permission_verbs).intersection(lemma_dict.keys()))
    anyTrue = way1 or way2 or way3
    if anyTrue == True:
        return 1
    else:
        return 0


def entitlement(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs,entitlement_verbs):
    
    way1 = "neg" not in dep_dict and any(set(entitlement_verbs).intersection(lemma_dict.keys()))

    way2 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and 'be' in lemma_dict

    way3 = "neg" in dep_dict and any(set(obligation_verbs).intersection(lemma_dict.keys()))

    anyTrue = way1 or way2 or way3
    if anyTrue == True:
        return 1
    else:
        return 0


def mandatory_delegation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs,entitlement_verbs):

    way1 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys()))

    anyTrue = way1
    if anyTrue == True:
        return 1
    else:
        return 0

def permissive_delegation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs,entitlement_verbs):

    way1 = "neg" not in dep_dict and any(set(permissive_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))

    anyTrue = way1
    if anyTrue == True:
        return 1
    else:
        return 0

def permissive_provision(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs,entitlement_verbs):

    way1 = "neg" not in dep_dict and any(set(permissive_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))

    anyTrue = way1
    if anyTrue == True:
        return 1
    else:
        return 0

def mandatory_provision(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs,entitlement_verbs):

    way1 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))

    anyTrue = way1
    if anyTrue == True:
        return 1
    else:
        return 0

def constraining_provision(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals,
                permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs,entitlement_verbs):

    way1 = "neg" in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))

    anyTrue = way1
    if anyTrue == True:
        return 1
    else:
        return 0

cols = ['name','citation','id','obligation', 'constraint','permission','entitlement','MandatoryDelegation',
        'Permissive Delegation', 'PermissiveProvision','MandatoryProvision', 'Constraining Provision']

# tokenize everything
docs = list(nlp.pipe(df.text))
provisions_lst = []

for index, provision in enumerate(docs):
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

df1.to_csv("provisions.csv")
