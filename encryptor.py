import abc
from collections import Counter
from math import fabs
import argparse
import json

from string import ascii_letters as ALPHABET
ALPHABET_SIZE = 26


class Coder:
    @abc.abstractmethod
    def __init__(self, key, key_len):
        self.key = key
        self.key_len = key_len

    @abc.abstractmethod
    def shift(self, letter):
        pass

    def en_de_code(self, text):
        new_text = []
        key_position = 0
        for simbol in text:
            if simbol in ALPHABET:
                new_text.append(self.shift(simbol, key_position))
                key_position = (key_position+1)%self.key_len
            else:
                new_text.append(simbol)
        return ''.join(new_text)

class CaesarEncoder(Coder):
    def __init__(self, key):
        key = int(key) % ALPHABET_SIZE
        super().__init__(key, 1)

    def shift(self, simbol, key_position: int):
        if ALPHABET.find(simbol) < ALPHABET_SIZE:
            return ALPHABET[(ALPHABET.find(simbol)+self.key)%ALPHABET_SIZE]
        else:
            return ALPHABET[(ALPHABET.find(simbol)-ALPHABET_SIZE+self.key)%ALPHABET_SIZE+ALPHABET_SIZE]

class CaesarDecoder(Coder):
    def __init__(self, key):
        key = int(key) % ALPHABET_SIZE
        super().__init__(key, 1)

    def shift(self, simbol, key_position: int):
        if ALPHABET.find(simbol) < ALPHABET_SIZE:
            return ALPHABET[(ALPHABET.find(simbol)-self.key)%ALPHABET_SIZE]
        else:
            return ALPHABET[(ALPHABET.find(simbol)-ALPHABET_SIZE-self.key)%ALPHABET_SIZE+ALPHABET_SIZE]

class VigenereEncoder(Coder):
    def __init__(self, key):
        key = key.lower()
        super().__init__(key, len(key))

    def shift(self, simbol, key_position: int):
        if ALPHABET.find(simbol) < ALPHABET_SIZE:
            return ALPHABET[(ALPHABET.find(simbol)+ALPHABET.find(self.key[key_position]))%ALPHABET_SIZE]
        else:
            return ALPHABET[(ALPHABET.find(simbol)+ALPHABET.find(self.key[key_position]))%ALPHABET_SIZE+ALPHABET_SIZE]

class VigenereDecoder(Coder):
    def __init__(self, key):
        key = key.lower()
        super().__init__(key, len(key))

    def shift(self, simbol, key_position: int):
        if ALPHABET.find(simbol) < ALPHABET_SIZE:
            return ALPHABET[(ALPHABET.find(simbol)-ALPHABET.find(self.key[key_position]))%ALPHABET_SIZE]
        else:
            return ALPHABET[(ALPHABET.find(simbol)-ALPHABET.find(self.key[key_position]))%ALPHABET_SIZE+ALPHABET_SIZE]


class Trainer():
    def __init__(self):
        self.model = {}
    
    def reset(self):
        self.model = {}

    def get_model(self, text):
        statistic = Counter(text)
        for item in statistic.elements():
            self.model[item] = 1.0*statistic[item]/sum(statistic.values())
        return (self.model)


class Hacker():
    def __init__(self, model):
        self.model = model

    def hack(self, text):
        trainer = Trainer()
        decoder = CaesarDecoder(0)
        right_key = 0
        train_model = trainer.get_model(decoder.en_de_code(text))
        difference = 0
        for item in train_model:
            if item[0] in self.model.keys():
                difference += fabs(self.model[item[0]]-train_model[item[0]])
            else:
                difference += fabs(train_model[item[0]])
        trainer.reset()
        for key in range(1, 26):
            decoder.key = key
            train_model = trainer.get_model(decoder.en_de_code(text))
            dist = 0
            for item in train_model:
                if item[0] in self.model.keys():
                    dist += fabs(self.model[item[0]]-train_model[item[0]])
                else:
                    difference += fabs(train_model[item[0]])
            if dist < difference:
                right_key = key
                difference = dist
            trainer.reset()
        decoder.key = right_key
        return decoder.en_de_code(text)



def encode(args):
    if args.cipher == 'caesar':
        encoder = CaesarEncoder(args.key)
    else:
        encoder = VigenereEncoder(args.key)
    
    if args.input_file:
        with open(args.input_file, 'r') as f:
            text = f.read()
    else:
        text = input()
    
    encoded_text = encoder.en_de_code(text)
    
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(encoded_text)
    else:
        print(encoded_text)

def decode(args):
    if args.cipher == 'caesar':
        decoder = CaesarDecoder(args.key)
    else:
        decoder = VigenereDecoder(args.key)
    
    if args.input_file:
        with open(args.input_file, 'r') as f:
            text = f.read()
    else:
        text = input()
    
    decoded_text = decoder.en_de_code(text)
    
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(decoded_text)
    else:
        print(decoded_text)

def train(args):
    trainer = Trainer()

    if args.text_file:
        with open(args.text_file, 'r') as f:
            text = f.read()
    else:
        text = input()

    model = trainer.get_model(text)

    if args.model_file:
        with open(args.model_file, 'w') as f:
            json.dump(model, f)
    else:
        print(model)

def hack(args):
    if args.input_file:
        with open(args.input_file, 'r') as f:
            text = f.read()
    else:
        text = input()
    
    with open(args.model_file, 'r') as f:
            model = json.load(f)
    
    hacker = Hacker(model)
    hacked_text = hacker.hack(text)

    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(hacked_text)
    else:
        print(hacked_text)



parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
subparsers = parser.add_subparsers()

parser_encode = subparsers.add_parser('encode')
parser_encode.set_defaults(mode = 'encode', function = encode, help='This will be working mode')
parser_encode.add_argument('--cipher', help='This will be the type of cipher', required = True)
parser_encode.add_argument('--key', help='This will be the key', required = True)
parser_encode.add_argument('--input-file',  help='This will be the input file')
parser_encode.add_argument('--output-file', help='This will be the output file')

parser_decode = subparsers.add_parser('decode')
parser_decode.set_defaults(mode = 'decode', function = decode, help='This will be working mode')
parser_decode.add_argument('--cipher', help='This will be the type of cipher', required = True)
parser_decode.add_argument('--key', help='This will be the key', required = True)
parser_decode.add_argument('--input-file',  help='This will be the input file')
parser_decode.add_argument('--output-file', help='This will be the output file')

parser_train = subparsers.add_parser('train')
parser_train.set_defaults(mode = 'train', function = train, help='This will be working mode')
parser_train.add_argument('--text-file', help='This will be the file with text to analyse')
parser_train.add_argument('--model-file', help='This will be the file for statistic')

parser_hack = subparsers.add_parser('hack')
parser_hack.set_defaults(mode = 'hack', function = hack, help='This will be working mode')
parser_hack.add_argument('--input-file',  help='This will be the input file')
parser_hack.add_argument('--output-file', help='This will be the output file')
parser_hack.add_argument('--model-file', help='This will be the file for statistic', required = True)

args = parser.parse_args()
args.function(args)