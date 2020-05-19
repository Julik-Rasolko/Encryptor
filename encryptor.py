import abc
from collections import Counter
from math import fabs
import argparse
import json

from string import ascii_letters as ALPHABET
ALPHABET_SIZE = int(len(ALPHABET)/2)


class Coder:
    def __init__(self, key, key_len):
        self.key = key
        self.key_len = key_len

    @abc.abstractmethod
    def shift(self, letter, key_position):
        pass

    def en_de_code(self, text):
        new_text = []
        key_position = 0
        for symbol in text:
            if symbol in ALPHABET:
                new_text.append(self.shift(symbol, key_position))
                key_position = (key_position+1) % self.key_len
            else:
                new_text.append(symbol)
        return ''.join(new_text)

    def super_shift(self, symbol, key):
        symbol_num = ALPHABET.find(symbol)
        if symbol_num < ALPHABET_SIZE:
            return ALPHABET[(symbol_num+key)%ALPHABET_SIZE]
        else:
            return ALPHABET[(symbol_num-ALPHABET_SIZE+key)%ALPHABET_SIZE+ALPHABET_SIZE]


class CaesarEnDecoder(Coder):
    def __init__(self, key):
        key = int(key) % ALPHABET_SIZE
        super().__init__(key, 1)

class CaesarEncoder(CaesarEnDecoder):
    def shift(self, symbol, key_position: int):
        return self.super_shift(symbol, self.key)

class CaesarDecoder(CaesarEnDecoder):
    def shift(self, symbol, key_position: int):
        return self.super_shift(symbol, -self.key)


class VigenereEnDecoder(Coder):
    def __init__(self, key):
        key = key.lower()
        super().__init__(key, len(key))

class VigenereEncoder(VigenereEnDecoder):
    def shift(self, symbol, key_position: int):
        return self.super_shift(symbol, ALPHABET.find(self.key[key_position]))

class VigenereDecoder(VigenereEnDecoder):
    def shift(self, symbol, key_position: int):
        return self.super_shift(symbol, -ALPHABET.find(self.key[key_position]))


class Trainer():
    def __init__(self):
        self.model = {}

    def get_model(self, text):
        statistic = Counter(text)
        for item in statistic.elements():
            self.model[item] = statistic[item] / sum(statistic.values())
        return self.model


class Hacker():
    def __init__(self, model):
        self.model = model

    def get_difference(self, train_model, key):
        difference = 0
        for symbol in train_model:
            shifted_symbol = ALPHABET[(ALPHABET.find(symbol)-key)%ALPHABET_SIZE]
            if shifted_symbol in self.model.keys():
                difference += fabs(self.model[shifted_symbol]-train_model[symbol])
            else:
                difference += fabs(train_model[symbol])
        return difference

    def hack(self, text):
        trainer = Trainer()
        right_key = 0
        train_model = trainer.get_model(text)
        min_difference = self.get_difference(train_model, 0)
        for key in range(1, ALPHABET_SIZE):
            difference = self.get_difference(train_model, key)
            if difference < min_difference:
                right_key = key
                min_difference = difference
        decoder = CaesarDecoder(right_key)
        return decoder.en_de_code(text)


def get_source(input_file):
    if input_file:
        with open(input_file, 'r') as f:
            text = f.read()
    else:
        text = input()
    return text

def deliver_result(output_file, text):
    if output_file:
        with open(output_file, 'w') as f:
            f.write(text)
    else:
        print(text)


def encode(args):
    if args.cipher == 'caesar':
        encoder = CaesarEncoder(args.key)
    else:
        encoder = VigenereEncoder(args.key)
    text = get_source(args.input_file)
    encoded_text = encoder.en_de_code(text)
    deliver_result(args.output_file, encoded_text)

def decode(args):
    if args.cipher == 'caesar':
        decoder = CaesarDecoder(args.key)
    else:
        decoder = VigenereDecoder(args.key)
    text = get_source(args.input_file)
    decoded_text = decoder.en_de_code(text)
    deliver_result(args.output_file, decoded_text)

def train(args):
    trainer = Trainer()
    text = get_source(args.text_file)
    model = trainer.get_model(text)
    if args.model_file:
        with open(args.model_file, 'w') as f:
            json.dump(model, f)
    else:
        print(model)

def hack(args):
    text = get_source(args.input_file)
    with open(args.model_file, 'r') as f:
            model = json.load(f)
    hacker = Hacker(model)
    hacked_text = hacker.hack(text)
    deliver_result(args.output_file, hacked_text)



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

