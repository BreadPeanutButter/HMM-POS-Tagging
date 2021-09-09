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
            add_to_dict(tag, word, emission_frequency, EMISSION_FREQ)
            add_to_dict(previous_tag, tag, transition_frequency, TRANSITION_FREQ)
            previous_tag = tag
            
        add_to_dict(previous_tag, END_OF_SENTENCE, transition_frequency, TRANSITION_FREQ)

    data = {TRANSITION_FREQ:transition_frequency, EMISSION_FREQ:emission_frequency, TOTAL_TOKEN_COUNT:total_tokens}
    with open(model_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(transition_frequency.keys())
    
    print('Finished...')

def add_to_dict(key1, key2, dictionary, attr):
    if key1 in dictionary:
        tag_data  = dictionary[key1]
        if key2 in tag_data:
                tag_data[ONE_OCCURENCE_COUNT] -= 1 if tag_data[key2] == 1 else 0
                tag_data[key2] += + 1
        else:
            tag_data[key2] = 1
            tag_data[ONE_OCCURENCE_COUNT] += 1

        if attr == EMISSION_FREQ:
            tag_data[CAPITALISED_COUNT] += 1 if key2[0].isupper() else 0
        
        tag_data[TOTAL_TAG_COUNT] += 1

    else:
        if attr == TRANSITION_FREQ:
            dictionary[key1] = {TOTAL_TAG_COUNT:1, ONE_OCCURENCE_COUNT: 1, key2:1} 
        elif attr == EMISSION_FREQ:
            count = 1 if key2[0].isupper() else 0
            dictionary[key1] = {TOTAL_TAG_COUNT:1, ONE_OCCURENCE_COUNT: 1, 
                                CAPITALISED_COUNT:count , key2:1} 

if __name__ == "__main__":
    # make no changes here
    train_file = sys.argv[1]
    model_file = sys.argv[2]
    start_time = datetime.datetime.now()
    train_model(train_file, model_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
