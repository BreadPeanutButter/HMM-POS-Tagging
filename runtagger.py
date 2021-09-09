# python3.8 runtagger.py <test_file_absolute_path> <model_file_absolute_path> <output_file_absolute_path>

import os
import math
import sys
import datetime
import json
import math
import re

# Tags for start and end of sentence
# Not part of the real set of tags
START_OF_SENTENCE = 'SOS'
END_OF_SENTENCE = 'EOS'

# Dictionary key constants
TOTAL_TAG_COUNT = '(TOTAL-TAG-COUNT)'
CAPITALISED_COUNT = '(CAPITALISED-WORD-COUNT)'
ONE_OCCURENCE_COUNT = '(ONE-OCCURENCE-COUNT)'
CARDINAL_NUMBER_COUNT = '(CARDINAL_NUMBER_COUNT)'
TOTAL_TOKEN_COUNT = 'total_token_count'

TRANSITION_FREQ = 'transition_frequency'
EMISSION_FREQ = 'emission_frequency'

NUMBER_REGEX = r'^[0-9\.\-,]*$'

SUFFIXES = ['ment', 'tion', 'sion',  'ance', 'ence', 'less', 'able', 'ness', 'ship',
'ery', 'ent', 'est', 'ive', 'ous', 'ful', 'ity', 'cy', 'ism', 'age', 'ial',
'nce', 'ise', 'ize', 'fy', 'en', 'ed', 'es', 'er', 'st', 'ing', 'ly', 'al', 's']

PUNCTUATION_TAGS = ['.', ',', ':', '$', '#', '``', "''"]

def tag_sentence(test_file, model_file, out_file):
    # write your code here. You can add functions as well.
    test_lines = open(test_file, 'r').readlines()
    model = json.load(open(model_file))
    out = open(out_file, "w")
    
    for line in test_lines:
        tokens = line.rstrip('\n').split()
        tagged_sentence = viterbi(tokens, model)
        out.write(tagged_sentence + '\n')
    
    print('Finished...')

# returns string of tokens with predicted tags
def viterbi(tokens, model):

    tag_list = list(model[TRANSITION_FREQ].keys())
    tag_list.remove(START_OF_SENTENCE) 

    max_log_prob = [0]*len(tag_list) 
    max_paths = [0]*len(tag_list)

    for idx, word in enumerate(tokens):
        if idx == 0:
            # Initialise arr with probability of P(T1|T0)P(W1|T1)
            for k, tag in enumerate(tag_list):
                transition = get_transition_prob(START_OF_SENTENCE, tag, model) 
                emission = get_emission_prob(tag, word, model)
                max_log_prob[k] = math.log(transition * emission) if emission * transition > 0 else -math.inf
                max_paths[k] = [f'{word}/{tag}']
            continue

        temp_prob_arr = [-math.inf]*len(tag_list)
        temp_path_arr = [[]]*len(tag_list)
        for i, curr_tag in enumerate(tag_list):
            tag2word_probability = get_emission_prob(curr_tag, word, model)
            if tag2word_probability == 0:
                continue
            for x, prev_tag in enumerate(tag_list):
                tag2tag_probability = get_transition_prob(prev_tag, curr_tag, model)
                if tag2tag_probability == 0:
                    continue
                log_probability = math.log(tag2word_probability * tag2tag_probability)
                if max_log_prob[x] + log_probability > temp_prob_arr[i]:
                    temp_prob_arr[i] = max_log_prob[x] + log_probability
                    temp_path_arr[i] = max_paths[x] + [f'{word}/{curr_tag}']

        max_log_prob = temp_prob_arr
        max_paths = temp_path_arr

    # Multiply EOS tag
    for idx, tag in enumerate(tag_list):
        eos_count = 0
        if END_OF_SENTENCE in model[TRANSITION_FREQ][tag]:
            eos_count = model[TRANSITION_FREQ][tag][END_OF_SENTENCE] 
        
        eos_prob = max([eos_count, 1]) / model[TRANSITION_FREQ][tag][TOTAL_TAG_COUNT]
        max_log_prob[idx] = max_log_prob[idx] + math.log(eos_prob)
    
    max_idx = max_log_prob.index(max(max_log_prob))
    return ' '.join(max_paths[max_idx])

def get_transition_prob(tag_prev, tag_curr, model):
    transition_freq = model[TRANSITION_FREQ]
    transition_prob = 0
    tag_prev_freq = transition_freq[tag_prev]
    if tag_curr in tag_prev_freq:
        transition_prob = tag_prev_freq[tag_curr] / tag_prev_freq[TOTAL_TAG_COUNT]
    else:
        transition_prob = tag_prev_freq[ONE_OCCURENCE_COUNT] / tag_prev_freq[TOTAL_TAG_COUNT]
    return transition_prob

def get_emission_prob(tag_curr, word, model):
    emission_freq = model[EMISSION_FREQ]
    emission_prob = 0
    tag_curr_freq = emission_freq[tag_curr]
    if word in tag_curr_freq:
        emission_prob = tag_curr_freq[word] / tag_curr_freq[TOTAL_TAG_COUNT]
    else:
        # Unknown word estimation
        if tag_curr in PUNCTUATION_TAGS:
            return 0
        
        capitalised_count = tag_curr_freq[CAPITALISED_COUNT] if word[0].isupper() \
        else tag_curr_freq[TOTAL_TAG_COUNT] - tag_curr_freq[CAPITALISED_COUNT]

        suffix_count = 0
        for suffix in SUFFIXES:
            if word.endswith(suffix):
                suffix_count = tag_curr_freq[f'(SUFFIX-{suffix})']
                break
        cardinal_count = 0
        if bool(re.match(NUMBER_REGEX, word)):
            cardinal_count = tag_curr_freq[CARDINAL_NUMBER_COUNT]
        suffix_count = max([suffix_count, 1])
        capitalised_count = max([capitalised_count, 1])
        one_occurence_count = max([tag_curr_freq[ONE_OCCURENCE_COUNT], 1])
        cardinal_count = max([cardinal_count, 1])

        emission_prob =  one_occurence_count / tag_curr_freq[TOTAL_TAG_COUNT] \
                        * capitalised_count / tag_curr_freq[TOTAL_TAG_COUNT] \
                        * suffix_count / tag_curr_freq[TOTAL_TAG_COUNT] \
                        * cardinal_count / tag_curr_freq[TOTAL_TAG_COUNT] \
                        * tag_curr_freq[TOTAL_TAG_COUNT] / model[TOTAL_TOKEN_COUNT] 

    return emission_prob


if __name__ == "__main__":
    # make no changes here
    test_file = sys.argv[1]
    model_file = sys.argv[2]
    out_file = sys.argv[3]
    start_time = datetime.datetime.now()
    tag_sentence(test_file, model_file, out_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
