import os
from collections import OrderedDict
from string import whitespace
from typing import Tuple

from sortedcontainers import SortedDict

from common.constants import DIVIDER, SPLIT, PATH_TO_DATA_DIR
from dictionary.tokenizer import Tokenizer

REGEXPS = {
    'ip_addres': r'([\\d]{1, 3}.){3}[\\d]{1, 3}}'
}

tokenizer = Tokenizer()


def get_list_of_files() -> enumerate:
    return enumerate(os.listdir(PATH_TO_DATA_DIR))


def split_chunk(chunk: str) -> Tuple[str, str]:
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


def get_tokens_from_chunk(chunk: str, chunk_start: int) -> list:
    return [(chunk_start + start, token)
            for start, token in tokenizer.tokenize(chunk)]


def iterable_to_str(iterable) -> str:
    return ','.join([str(item) for item in iterable])


def dict_to_str(dictionary: OrderedDict) -> str:
    return '\t'.join([f'{key}|{value}' for key, value in dictionary.items()])


def write_dictionary_to_file(dictionary: SortedDict, path: str,
                             is_lexicon=False) -> None:
    print(f'Writing dict of size {len(dictionary)} to {path}')

    with open(path, 'w') as result_file:
        for key, values in dictionary.items():
            documents = iterable_to_str(values)
            key = f'{key}{DIVIDER + str(len(values)) if is_lexicon else "" }'
            result_file.write(f'{key}{SPLIT}{documents}\n')


def write_token_list_to_file(token_list: OrderedDict, path: str) -> None:
    print(f'Writing dict of size {len(token_list)} to {path}')

    with open(path, 'w') as result_file:
        for key in token_list:
            token_inputs = iterable_to_str(token_list[key])
            result_file.write(f'{key}{SPLIT}{token_inputs}\n')


def write_doc_ids_to_file(file_doc_id: dict, path: str) -> None:
    with open(path, 'w') as file:
        for key in file_doc_id:
            file.write(f'{key}{SPLIT}{file_doc_id[key]}\n')
