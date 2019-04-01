from enum import Enum

from bool_search.skip_list_search import DocumentSkipList, SearchDictionary, \
    OPERATION_CODES, ALL
from common.constants import SPLIT, DIVIDER, PATH_TO_DICT
from common.exceptions import IncorrectQuery
from dictionary.tokenizer import Tokenizer


class OPERATIONS:
    AND = ['AND']
    OR = ['OR', '|']
    NOT = ['-']
    AND_OR = AND + OR
    ALL = AND_OR + NOT


def load_inverted_skip_index(path: str = PATH_TO_DICT) -> SearchDictionary:
    """
    Reads inverted index(dictionary) from file. The proposed data
    structure to save dictionary:
                 ___________________________________   _________________
                |                                   | |                 |
                |                                   V |                 V
    token -> (doc_id1->doc_id2->doc_id3->doc_id4->doc_id5->doc_id6->doc_id6)
    This data structure accelerate the search
    :param path: path to file on disk with inverted index
    :return inverted index (dictionary)
    """
    result = dict()
    with open(path) as file:
        for line in file:
            key, values = line.strip().split(SPLIT)
            # omit frequency in this case
            token, _ = key.split(DIVIDER)
            result[token] = DocumentSkipList(values.split(','))
    return SearchDictionary(result)


def get_operator_code(operator) -> OPERATION_CODES:
    if operator in OPERATIONS.AND:
        return OPERATION_CODES.AND
    elif operator in OPERATIONS.OR:
        return OPERATION_CODES.OR
    elif operator in OPERATIONS.NOT:
        return OPERATION_CODES.NOT
    raise NotImplementedError(
        f'Operator "{operator}" is not supported')


def build_notation_from_normalized_query(query: str) -> list:
    def tokenize(word: str) -> str:
        word = tokenizer.tokenize(word)
        return token[0][1] if word else ALL

    def add_token_to_notation():
        if token.startswith(OPERATIONS.NOT[0]) and len(token) > 1:
            result_notation.append(tokenize(token[1:]))
            result_notation.append(OPERATION_CODES.NOT)
        else:
            result_notation.append(tokenize(token))

    states = Enum(('states', 'START TOKEN OPERATOR'))
    result_notation = list()
    stack = list()
    tokenizer = Tokenizer()
    state = states.START
    for token in query.split(' '):
        if state == states.START and token in OPERATIONS.AND_OR:
            raise IncorrectQuery(query, query.index(token))
        elif state == states.START:
            state = states.TOKEN
            add_token_to_notation()
        elif state == states.TOKEN and token in OPERATIONS.AND_OR:
            state = states.OPERATOR
            stack.append(get_operator_code(token))
        elif state == states.TOKEN:
            stack.append(get_operator_code(OPERATIONS.AND[0]))
            add_token_to_notation()
        elif state == states.OPERATOR and token in OPERATIONS.AND_OR:
            raise IncorrectQuery(query, query.index(token))
        elif state == states.OPERATOR:
            state = states.TOKEN
            add_token_to_notation()
        else:
            raise IncorrectQuery(query, query.index(token))
    if state == states.OPERATOR:
        raise IncorrectQuery(query, len(query))
    while len(stack) > 0:
        result_notation.append(stack.pop())
    return result_notation


def remove_extra_spaces(line: str) -> str:
    return ' '.join(line.strip().split())


def build_notation(command: str) -> list:
    """
    Convert command to an inverted notation.
    :param command: search query string. All operands must be separated
    by spaces
    :return: inverted notation
    """
    if command == '' or command is None:
        return list()
    normalized_command = remove_extra_spaces(command)
    if normalized_command == '':
        return list()

    return build_notation_from_normalized_query(normalized_command)
