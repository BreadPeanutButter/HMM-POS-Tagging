# python3.8 buildtagger.py <train_file_absolute_path> <model_file_absolute_path>

import os
import math
import sys
import datetime
import json

# Tags for start and end of sentence
# Not part of the real set of tags
START_OF_SENTENCE = 'SOS'
END_OF_SENTENCE = 'EOS'

# Dictionary key constants
TOTAL_TAG_COUNT = '(TOTAL-TAG-COUNT)' 
CAPITALISED_COUNT = '(CAPITALISED-WORD-COUNT)'
ONE_OCCURENCE_COUNT = '(ONE-OCCURENCE-COUNT)'
TOTAL_TOKEN_COUNT = 'total_token_count'

TRANSITION_FREQ = 'transition_frequency'
EMISSION_FREQ = 'emission_frequency'

SUFFIX_ED = '(SUFFIX-ed)'
SUFFIX_S = '(SUFFIX-s)'
SUFFIX_ES = '(SUFFIX-es)'
SUFFIX_ING = '(SUFFIX-ing)'
SUFFIX_LY = '(SUFFIX-ly)'
SUFFIX_ER = '(SUFFIX-er)'
SUFFIX_ST = '(SUFFIX-st)'
SUFFIX_EST = '(SUFFIX-est)'
SUFFIX_IAL = '(SUFFIX-ial)'
SUFFIX_AL = '(SUFFIX-al)'
SUFFIX_ENT = '(SUFFIX-ent)'
SUFFIXES = ['ed', 'es', 'er', 'st', 's', 'ing', 'ly', 'est', 'ial', 'al', 'ent']


def train_model(train_file, model_file):
    # write your code here. You can add functions as well.

    transition_frequency = {} # Count of Ti|Ti-1 with key Ti-1
    emission_frequency = {} # Count of Wi|Ti occurunces with key Ti
    total_tokens = 0

    file = open(train_file, 'r')
    lines = file.readlines()

    for line in lines:
        previous_tag = START_OF_SENTENCE
        tokens = line.rstrip('\n').split()
        total_tokens += len(tokens)

        for token in tokens:
            word, tag = token.rsplit(sep='/', maxsplit=1)
            add_emission_freq(tag, word, emission_frequency)
            add_transition_freq(previous_tag, tag, transition_frequency)
            previous_tag = tag
            
        add_transition_freq(previous_tag, END_OF_SENTENCE, transition_frequency)

    data = {TRANSITION_FREQ:transition_frequency, EMISSION_FREQ:emission_frequency, TOTAL_TOKEN_COUNT:total_tokens}
    with open(model_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(transition_frequency.keys())
    
    print('Finished...')

def add_emission_freq(curr_tag, word, dictionary):
    if curr_tag in dictionary:
        tag_data  = dictionary[curr_tag]
        if word in tag_data:
            tag_data[word] += + 1
            tag_data[ONE_OCCURENCE_COUNT] -= 1 if tag_data[word] == 1 else 0    
        else:
            tag_data[word] = 1
            tag_data[ONE_OCCURENCE_COUNT] += 1

         
        tag_data[TOTAL_TAG_COUNT] += 1

    else:
        dictionary[curr_tag] = {TOTAL_TAG_COUNT:1, ONE_OCCURENCE_COUNT: 1, 
                                CAPITALISED_COUNT:0, SUFFIX_ED:0, SUFFIX_S:0,
                                SUFFIX_ES: 0, SUFFIX_ING:0, SUFFIX_LY:0,
                                SUFFIX_ER:0, SUFFIX_ST:0, SUFFIX_EST:0,
                                SUFFIX_IAL:0, SUFFIX_AL:0, SUFFIX_ENT:0,
                                word:1} 
        tag_data  = dictionary[curr_tag]

    tag_data[CAPITALISED_COUNT] += 1 if word[0].isupper() else 0

    for suffix in SUFFIXES:
        if word.endswith(suffix):
            tag_data[f'(SUFFIX-{suffix})'] += 1
            

def add_transition_freq(prev_tag, curr_tag, dictionary):
    if prev_tag in dictionary:
        tag_data  = dictionary[prev_tag]
        if curr_tag in tag_data:
                tag_data[ONE_OCCURENCE_COUNT] -= 1 if tag_data[curr_tag] == 1 else 0
                tag_data[curr_tag] += + 1
        else:
            tag_data[curr_tag] = 1
            tag_data[ONE_OCCURENCE_COUNT] += 1
    else:
        dictionary[prev_tag] = {TOTAL_TAG_COUNT:1, ONE_OCCURENCE_COUNT: 1, curr_tag:1} 
        
    

if __name__ == "__main__":
    # make no changes here
    train_file = sys.argv[1]
    model_file = sys.argv[2]
    start_time = datetime.datetime.now()
    train_model(train_file, model_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
