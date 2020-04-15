from collections import Counter
from math import fabs
import argparse
import json
from string import ascii_letters as alphabet


def Encode(cipher, key, text):
    text = list(text)
    if cipher == 'caesar':
        key = int(key)
        for i in range(len(text)):
            if alphabet.find(text[i]) != -1:
                if alphabet.find(text[i]) < 26:
                    text[i] = alphabet[(alphabet.find(text[i])+key)%26]
                else:
                    text[i] = alphabet[(alphabet.find(text[i])-26+key)%26+26]
    elif cipher == 'vigenere':
        V_index = 0
        for i in range(len(text)):
            if alphabet.find(text[i]) != -1:
                if alphabet.find(text[i]) < 26:
                    text[i] = alphabet[(alphabet.find(text[i])+alphabet.find(key[V_index%len(key)]))%26]
                else:
                    text[i] = alphabet[(alphabet.find(text[i])-26+alphabet.find(key[V_index%len(key)]))%26+26]
                V_index += 1
    return ''.join(text)

def Decode(cipher, key, text):
    text = list(text)
    if cipher == 'caesar':
        key = int(key)
        for i in range(len(text)):
            if alphabet.find(text[i]) != -1:
                if alphabet.find(text[i]) < 26:
                    text[i] = alphabet[(alphabet.find(text[i])-key)%26]
                else:
                    text[i] = alphabet[(alphabet.find(text[i])-26-key)%26+26]
    elif cipher == 'vigenere':
        V_index = 0
        for i in range(len(text)):
            if alphabet.find(text[i]) != -1:
                if alphabet.find(text[i]) < 26:
                    text[i] = alphabet[(alphabet.find(text[i])-alphabet.find(key[V_index%len(key)]))%26]
                else:
                    text[i] = alphabet[(alphabet.find(text[i])-26-alphabet.find(key[V_index%len(key)]))%26+26]
                V_index += 1
    return ''.join(text)

def Train(text):
    stat = Counter(text)
    statistic = {}
    for item in stat.elements():
        statistic[item] = 1.0*stat[item]/sum(stat.values())
    return (statistic.items())

def Hack(model, text):
    model = dict(model)
    right_key = 0
    statistic = Train(Decode('caesar', 0, text))
    dist = 0
    for item in statistic:
        if item[0] in model.keys():
            dist += fabs(model[item[0]]-item[1])
    difference = dist
    for key in range(26):
        statistic = Train(Decode('caesar', key, text))
        dist = 0
        for item in statistic:
            if item[0] in model.keys():
                dist += fabs(model[item[0]]-item[1])
        if dist < difference:
            right_key = key
            difference = dist
    return Decode('caesar', right_key, text)
        

def Get_result(mode, cipher, key, model_file, text):
    if mode == 'encode': 
        return Encode(cipher, key, text)
    elif mode == 'decode': 
        return Decode(cipher, key, text)
    elif mode == 'train': 
        return Train(text)
    elif mode == 'hack':
        return Hack(model, text)


parser = argparse.ArgumentParser()
parser.add_argument('mode', help='This will be working mode')
parser.add_argument('--cipher', help='This will be the type of cipher')
parser.add_argument('--key', help='This will be the key')
parser.add_argument('--input-file',  help='This will be the input file')
parser.add_argument('--output-file', help='This will be the output file')
parser.add_argument('--text-file', help='This will be the file with text to analyse')
parser.add_argument('--model-file', help='This will be the file for statistic')
args = parser.parse_args()


try:
    f = open(args.input_file, 'r')
    text = f.read()
    f.close()
except TypeError:
    try:
        f = open(args.text_file, 'r')
        text = f.read()
        f.close()
    except TypeError:
        text = input()

try:
    f = open(args.model_file, 'r')
    model = json.load(f)
    f.close()
except TypeError:
    model = ''

result = Get_result(args.mode, args.cipher, args.key, model, text)

try:
    f = open(args.output_file, 'w')
    f.write(result)
    f.close()
except TypeError:
    try:
        f = open(args.model_file, 'w')
        json.dump(result, f)
        f.close()
    except TypeError:
        print(result)
