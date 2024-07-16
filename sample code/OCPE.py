#!/usr/bin/python
# -*- coding: utf-8 -*-

# install spacy: https://spacy.io/usage/
# pandas should already be installed

import spacy
import pandas as pd
import re
import os
import glob
import argparse

parser = argparse.ArgumentParser()
#add date arguments -begin -b -end -e
parser.add_argument('-filepath','-f', action = 'append', help = 'Put the path here')
parser.add_argument('-ending','-e', action = 'append', help = 'End of filepath for csv')

args = parser.parse_args()

if vars(args)['filepath'] is None: 
	print "I'm assuming you wanted your home computer"
	path = '/Users/stevenrashin/Desktop/test/'
else:
	path = ', '.join(vars(args)['filepath'])

if vars(args)['ending'] is None: 
	print "I'm assuming you wanted your home computer"
	end1 = '-FR'
else:
	end1 = ', '.join(vars(args)['ending'])


print path

def separate_preamble(path):
    doc = unicode(open(path).read().decode('utf8'))
    rule_copy = doc.lower()

    rule_loc = find_all(rule_copy, 'text of rule')

    if rule_loc != []:
        rule_loc = max(rule_loc)

    if rule_loc == []:
        rule_loc = find_all(rule_copy, 'list of subjects')
        if rule_loc != []:
            rule_loc = max(rule_loc)

    if rule_loc == []:
        rule_loc = find_all(rule_copy, 'statutory authority')
        if rule_loc != []:
            rule_loc = max(rule_loc)

    if rule_loc == []:
        print "No way to parse rule text, go onto the next iteration"
        rule_portion = ""
        return rule_portion

    rule_portion = doc[rule_loc:]   

    return rule_portion


#path = '/Users/stevenrashin/Desktop/test/'
rules = glob.glob(path + "*.txt")

#load the parser, can load a larger parser

nlp = spacy.load('en')

# nlp.sm = spacy.load("en_core_web_sm")
# nlp.md = spacy.load("en_core_web_md")

#List the modals

strict_modals = ['shall','must','will']
permissive_modals = ['may', 'can']
other_modals = ['should', 'would', 'could', 'might']
obligation_verbs = ['require', 'expect', 'compel','oblige','obligate','have to','ought to']
constraint_verbs = ['prohibit','forbid','ban','bar','restrict','proscribe']
permission_verbs = ['allow','permit','authorize']
entitlement_verbs = ['have','receive', 'retain']
special_verbs = obligation_verbs + constraint_verbs + permission_verbs + entitlement_verbs

#create all the functions
#for the functions all have the same input (even the unused args) to make calling function easier

def obligation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals, permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs, entitlement_verbs):
    #this is an orderless version of an obligation, to add order to this use the code below
    #int(dep_dict['neg']) > int(tokentg_dict['MD'])
    
    #the code like structures from the paper are below
    #way1 = not item['neg'] and item['strict_modal'] and item['active_verb']
    #way2 = not item['neg'] and item['strict_modal'] and item['obligation_verb']
    #way3 = not item['neg'] and not item['md'] and item['obligation_verb']
    
    if "neg" in dep_dict:
        return 0
    else:
        way1 = any(set(strict_modals).intersection(lemma_dict.keys())) and 'be' not in lemma_dict
        #and "VERB" in speech_dict
        #and 'be' not in lemma_dict
        #item['strict_modal'] and item['active_verb']
        way2 = any(set(strict_modals).intersection(lemma_dict.keys())) and any(set(obligation_verbs).intersection(lemma_dict.keys()))
        #item['strict_modal'] and item['obligation_verb']
        way3 = 'MD' not in tokentg_dict and any(set(obligation_verbs).intersection(lemma_dict.keys()))
        #not item['md'] and item['obligation_verb']
        
        #put it all together, if we have one then we have an obligation
        anyTrue = way1 or way2 or way3
        if anyTrue == True:
            return 1
        else:
            return 0

def constraint(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals, permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs, entitlement_verbs):
    #item['neg'] and item['md'] and not item['obligation_verb']
    #not item['neg'] and item['strict_modal'] and item['constraint_verb']
    #item['neg'] and item['permission_verb']
    way1 = "neg" in dep_dict and 'MD' in tokentg_dict and not any(set(obligation_verbs).intersection(lemma_dict.keys()))
    
    way2 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and any(set(constraint_verbs).intersection(lemma_dict.keys()))
    
    way3 = "neg" in dep_dict and any(set(permission_verbs).intersection(lemma_dict.keys())) 
    
    anyTrue = way1 or way2 or way3
    if anyTrue == True:
        return 1
    else:
        return 0

def permission(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals, permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs, entitlement_verbs):
	# not item['neg'] and item['permission_verb']
	# not item['neg'] and item['permissive_modal'] and not item['special_verb']
	# What are special verbs?  
	# special verbs, namely those verbs which often appear in legal documents as associated with 
	# the provision types mentioned above. 
	# For instance, an obligation will contain verbs such as 'require', 'expect' and so on.
	# an action verb (i.e. any verb which is not among the special verbs identified above).
	# item['neg'] and item['constraint_verb']
	way1 = "neg" not in dep_dict and any(set(permission_verbs).intersection(lemma_dict.keys()))
    
	way2 = "neg" not in dep_dict and any(set(permissive_modals).intersection(lemma_dict.keys())) and not any(set(special_verbs).intersection(lemma_dict.keys()))
    
	way3 = "neg" in dep_dict and any(set(constraint_verbs).intersection(lemma_dict.keys())) 
	
	anyTrue = way1 or way2 or way3
	
	if anyTrue == True:
		return 1
	else:
		return 0

def entitlement(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals, permissive_modals, other_modals, obligation_verbs, contraint_verbs, permission_verbs, entitlement_verbs):
	#not item['neg'] and item['entitlement_verb']
	#not item['neg'] and item['strict_modal'] and item['passive']
	#item['neg'] and item['obligation_verb']
	
	way1 = "neg" not in dep_dict and any(set(entitlement_verbs).intersection(lemma_dict.keys()))
	
	way2 = "neg" not in dep_dict and any(set(strict_modals).intersection(lemma_dict.keys())) and 'be' in lemma_dict 
    
	way3 = "neg" in dep_dict and any(set(obligation_verbs).intersection(lemma_dict.keys())) 
	
	anyTrue = way1 or way2 or way3
	if anyTrue == True:
		return 1
	else:
		return 0
        

#error#
#rl = '/Users/stevenrashin/Desktop/test/Register--2011-17100--yydate2011-07-07yyagency-2011-17100-Notice.txt'
# rl = "/Users/stevenrashin/Dropbox/Federal-Reserve-Project/rules/Register--2013-31511--yydate2014-01-31yyagency-R-1432-Rule.txt"


#now set up the data frame

cols = ['type','length','date','docket-No','fr-doc-no','obligation', 'constraint', 'permission','entitlement','agency_obligation','agency_constraint', 'agency_permission','agency_entitlement','entity_obligation','entity_constraint', 'entity_permission','entity_entitlement']
provisions_lst = []

for rl in rules:

	print rl

	doc = unicode(open(rl).read().decode('utf8'))

	doc = separate_preamble(doc)

	doc_length = len(doc.split())
	
	if doc_length>300000:
		print "Document too long and coder too lazy to loop over portions of document"
		continue

	doc = nlp(doc)
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


	for sent in doc.sents:
		#create dictionaries because we need both the tag and the position since the code requires that certain elements
		#OPTIONAL: we need to relate each tag to its position in the sentence
		#dicts are orderless (lists are not) but have the same info, if you doubt this the code below will work
		#import operator
		#sorted_dep_dict = sorted(dep_dict.items(), key=operator.itemgetter(1))

		dep_dict = {}
		tokentg_dict = {}
		lemma_dict = {}
		token_dict = {}
		speech_dict = {}

		for token in sent:
			#print token.sentiment
			dep_dict[token.dep_] = token.i
			tokentg_dict[token.tag_] = token.i
			lemma_dict[token.lemma_] = token.i
			token_dict[token.text] = token.i
			speech_dict[token.pos_] = token.i

		obl = (obligation(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals, permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs, entitlement_verbs))
		const = constraint(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals, permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs, entitlement_verbs)
		permis = permission(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals, permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs, entitlement_verbs)
		entitle = entitlement(dep_dict, tokentg_dict, lemma_dict, token_dict, speech_dict, special_verbs, strict_modals, permissive_modals, other_modals, obligation_verbs, constraint_verbs, permission_verbs, entitlement_verbs)
		obligation_lst.append(obl)
		constraint_lst.append(const)
		permission_lst.append(permis)
		entitlement_lst.append(entitle)
		if obl == 0 & const == 0 & const == 0 & entitle == 0:
			continue
		#Now if there is an obligation... figure out who its on      
		for chunk in sent.noun_chunks:
			print chunk
			if chunk.root.dep_ == "nsubj":
				#bool is a T/F wrapper for re.search [A-Z]{3,}
				if bool(re.search(u'agency|commission|board|agencies', chunk.lemma_))|bool(re.search(u'[A-Z]{3,}', chunk.text)):
					print chunk.text
					if obl == 1:
						agency_obligation_lst.append(1)
					if const == 1:
						agency_constraint_lst.append(1)
					if permis == 1:
						agency_permission_lst.append(1)
					if entitle == 1:
						agency_entitlement_lst.append(1)
						#print chunk.lemma_
				if not (bool(re.search(u'[A-Z]{3,}', chunk.text))& bool(re.search(u'agency|commission|board|agencies', chunk.lemma_))&bool(re.search(u'-PRON-', chunk.text))):
					print chunk.text
					if obl == 1:
						entity_obligation_lst.append(1)
					if const == 1:
						entity_constraint_lst.append(1)
					if permis == 1:
						entity_permission_lst.append(1)
					if entitle == 1:
						entity_entitlement_lst.append(1)


	if re.search(pattern=r'ProposedRule|Rule|Notice', string=rl) is None:
		type = "N/A"
	else:
		type = re.search(pattern=r'ProposedRule|Rule|Notice', string=rl).group()

	if re.search(pattern=r'\d+-\d+-\d+', string=rl) is None:
		date = "N/A"
	else:
		date = re.search(pattern=r'\d+-\d+-\d+', string=rl).group()

	if re.search(pattern=r'R-\d+|OP-\d+|S\d+-\d+-\d+', string=rl) is None:
		agency_no = "N/A"
	else:
		agency_no = re.search(pattern=r'R-\d+|OP-\d+|S\d+-\d+-\d+', string=rl).group()

	if re.search(pattern=r'\d{4}-\d+', string=rl) is None:
		agency_no2 = "N/A"
	else:
		agency_no2 = re.search(pattern=r'\d{4}-\d+', string=rl).group()


	provisions_lst.append([type, doc_length, date, agency_no, agency_no2, sum(obligation_lst),sum(constraint_lst),sum(permission_lst),sum(entitlement_lst), sum(agency_obligation_lst),sum(agency_constraint_lst),sum(agency_permission_lst),sum(agency_entitlement_lst),sum(entity_obligation_lst),sum(entity_constraint_lst),sum(entity_permission_lst),sum(entity_entitlement_lst)])

df1 = pd.DataFrame(provisions_lst, columns=cols)

nms = "DF-Rules" + end1 + ".csv"

df1.to_csv(nms)

print df1
