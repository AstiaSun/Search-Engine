import os
from collections import OrderedDict
from string import whitespace
from typing import Tuple

from sortedcontainers import SortedDict

from dictionary.tokenizer import Tokenizer

PATH_TO_DIR = os.path.join(os.curdir, 'files')

REGEXPS = {
    'ip_addres': r'([\\d]{1, 3}.){3}[\\d]{1, 3}}'
}

PUNCTUATION = '.,!?;:'

tokenizer = Tokenizer()


def get_list_of_files():
    return enumerate(os.listdir(PATH_TO_DIR))


def split_chunk(chunk: str):
    position = 1
    for position, char in enumerate(reversed(chunk)):
        if not char.isalnum():
            break
    return chunk[:-position - 1], chunk[-position - 1:]


def add_unfinished_part_from_prev_chunk(chunk, unfinished_part
                                        ) -> Tuple[str, str]:
    chunk = unfinished_part + chunk
    return split_chunk_by_last_line(chunk)


def split_chunk_by_last_line(chunk) -> Tuple[str, str]:
    position = len(chunk) - 1
    while (position > 0) and (chunk[position] not in whitespace):
        position -= 1

    if position == 0:
        return chunk, ''
    return chunk[:position], chunk[position + 1:]


def get_tokens_from_chunk(chunk: str, chunk_start: int):
    return [(chunk_start + start, token)
            for start, token in tokenizer.tokenize(chunk)]


def iterable_to_str(iterable) -> str:
    return ','.join([str(item) for item in iterable])


def dict_to_str(dictionary: OrderedDict) -> str:
    return '\t'.join([f'{key}|{value}' for key, value in dictionary.items()])


def write_lexicon_to_file(lexicon: SortedDict, path: str):
    print(f'Writing dict of size {len(lexicon)} to {path}')

    with open(path, 'w') as result_file:
        for key in lexicon:
            documents = iterable_to_str(lexicon[key])
            result_file.write(f'{key}\t{documents}\n')


def write_token_list_to_file(token_list: OrderedDict, path: str):
    print(f'Writing dict of size {len(token_list)} to {path}')

    with open(path, 'w') as result_file:
        for key in token_list:
            token_inputs = iterable_to_str(token_list[key])
            result_file.write(f'{key}\t{token_inputs}\n')


def write_doc_ids_to_file(file_doc_id: dict, path: str):
    with open(path, 'w') as file:
        for key in file_doc_id:
            file.write(f'{key}\t{file_doc_id[key]}\n')
