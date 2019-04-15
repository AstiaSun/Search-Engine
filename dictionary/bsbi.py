"""
Implementation of a blocked sort-based indexing (BSBI)
Pre-conditions:
- Block - maximum amount of the records to easily save in RAM. Must be
able to contain tens of block in RAM.

Algorithm:

1. Form pairs <termID - docID> and colled them in memory while block is
not overwhelmed.
2. Block is inverted and saved on the disk.
Inverting is done in two phases:
    - Pairs <termID - docID> are sorted
    - All pairs with a common termID form inverted index.
3. Merge tens of blocks into one.
"""
import os
from typing import Tuple

from sortedcontainers import SortedList, SortedSet

from common.constants import BYTE, PATH_TO_RESULT_DIR, PATH_TO_DICT
from common.constants import SPLIT
from dictionary.decoder import get_file_reader_by_extension
from dictionary.utils import get_list_of_files, \
    add_unfinished_part_from_prev_chunk, get_tokens_from_chunk

MAX_BLOCK_SIZE = 10e4 * 12 * BYTE


def parse_next_block(doc_id, file_name) -> list:
    with get_file_reader_by_extension(file_name) as document:
        block = list()
        chunk_start = 0
        unfinished_part = ''
        chunk = document.read_chunk()
        while chunk:
            actual_chunk, unfinished_part = \
                add_unfinished_part_from_prev_chunk(chunk, unfinished_part)
            tokens = get_tokens_from_chunk(chunk, chunk_start)
            i = 0
            while i < len(tokens):
                for _ in range(min(MAX_BLOCK_SIZE - len(block), len(tokens))):
                    block.append(f'{tokens[i][1]}{SPLIT}{doc_id}')
                    i += 1
                if len(block) >= MAX_BLOCK_SIZE:
                    yield block
                    block = list()
            chunk = document.read_chunk()
            chunk_start += len(actual_chunk) + 1
        if unfinished_part:
            block.append(f'{unfinished_part}{SPLIT}{doc_id}')
        yield block


def bsbi_invert(block: list) -> list:
    def inverted_list_to_str(x) -> str:
        return f'{x}{SPLIT}{",".join(inverted_list[x])}'

    sorted(block)
    inverted_list = dict()
    for record in block:
        term_id, doc_id = record.split(SPLIT)
        if term_id not in inverted_list:
            inverted_list[term_id] = SortedList()
        inverted_list[term_id].append(doc_id)
    return list(map(inverted_list_to_str, inverted_list.keys()))


def write_block_to_disk(block: list, file_name: str):
    file_name = file_name if file_name.startswith(PATH_TO_RESULT_DIR) \
        else os.path.join(PATH_TO_RESULT_DIR, file_name)
    with open(file_name, 'w+') as inverted_file:
        inverted_file.writelines(block)


def read_inverted_index_by_line(path: str) -> Tuple[str, list]:
    with open(path) as file:
        for line in file.readlines():
            token_id, doc_ids = line.split(SPLIT)
            yield token_id, doc_ids.strip().split(',')


def merge_blocks(parts: list, merged_file_name: str = PATH_TO_DICT):
    chunk_parts_iter = 10
    inverted_index = dict()
    for k in range(len(parts) // 10 + int(len(parts) % 10 > 0)):
        chunk_start = k * chunk_parts_iter
        chunk_end = (k + 1) * chunk_parts_iter
        chunk_parts = parts[chunk_start: min(chunk_end, len(parts))]
        for file in chunk_parts:
            for token_id, doc_ids in read_inverted_index_by_line(file):
                if token_id not in inverted_index:
                    inverted_index[token_id] = SortedSet()
                inverted_index[token_id] += set(doc_ids)
    with open(merged_file_name, 'w+') as result:
        result.writelines(map(
            lambda x: f'{x}{SPLIT}{inverted_index[x]}', inverted_index))


def bsbi_index_construction():
    n = 0
    for file_id, file_name in get_list_of_files():
        for block in parse_next_block(file_id, file_name):
            inverted_block = bsbi_invert(block)
            write_block_to_disk(inverted_block, f'part{n}')
            n += 1
    merge_blocks(list(range(n)))
