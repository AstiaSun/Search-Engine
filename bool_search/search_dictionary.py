from dataclasses import dataclass
from enum import Enum
from typing import Optional

from common.constants import PATH_TO_LIST_OF_FILES, SPLIT
from dictionary.tokenizer import Tokenizer

OPERATION_CODES = Enum('OPERATION_CODES', 'AND OR NOT')
ALL = '*'


@dataclass
class DocumentNode:
    id: int
    # For memory optimisation None is used.
    # if field is None the next index is considered to be the
    # following item in the list
    next_id_index: Optional[int]

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __str__(self):
        return f'<{self.id, self.next_id_index}>'


class DocumentSkipList:
    """
    Proposed structure of skip list:
                            4                          7
               ___________________________   _____________________
              |                           | |                     |
              |                           V |                     V
    token->(doc_id1->doc_id2->doc_id3->doc_id4->doc_id5->doc_id6->doc_id7->doc_id8)
    This data structure accelerates the search of common documents
    in the dictionary.
    """

    def __init__(self, doc_ids=None):
        self.doc_ids = list()
        # every 4 of 5 items in list are skipped
        self.skip_number = 5
        self.last_not_skipped_node = 0
        self.add_list(doc_ids)

    def add_list(self, doc_ids: list) -> None:
        """
        Append a list of items to the skip list
        :param doc_ids: array of document ids
        """
        if doc_ids is None:
            return
        for doc_id in doc_ids:
            self.add(int(doc_id))

    def add(self, doc_id: int) -> None:
        """
        Appends the document id to the list of documents. if a new node
        is N-th skipped one, then the last node which has been marked
        as not skipped is assigned with a reference to the new node.
        The new node is marked as last not skipped.

        :param doc_id: id of the document
        """
        next_index = len(self.doc_ids)
        if self.last_not_skipped_node + self.skip_number == next_index:
            self.doc_ids[self.last_not_skipped_node].next_id_index = next_index
            self.last_not_skipped_node = next_index
        self.doc_ids.append(DocumentNode(doc_id, None))

    def skip_until_ge(self, index: int, other_value) -> int:
        """
        Skips nodes in skip list until the value of node is greater then
        or equal to the provided value [other_value]
        :param index: current index of list
        :param other_value: value to compare with
        :return: index of node in list which value is greater then of
        equal to the provided value [other_value]
        """
        while index < len(self) and self[index] < other_value:
            next_index = self[index].next_id_index \
                if self[index].next_id_index else index + 1
            while next_index < len(self) and self[next_index] < other_value:
                next_index = self[next_index].next_id_index \
                    if self[next_index].next_id_index else next_index + 1
            index = next_index
        return index

    def to_str(self) -> str:
        """
        returns string representation of list with documents ids only
        """
        return ','.join([str(node.id) for node in self.doc_ids])

    def to_list(self) -> list:
        return [node.id for node in self.doc_ids]

    def __iter__(self):
        return iter(self.doc_ids)

    def __len__(self):
        return len(self.doc_ids)

    def __getitem__(self, item):
        return self.doc_ids[item]

    def __setitem__(self, key, value):
        self.doc_ids[key] = value

    def __str__(self):
        return str(self.doc_ids)


class SearchDictionary:
    def __init__(self, inverted_index: dict):
        def get_all_file_ids() -> DocumentSkipList:
            with open(PATH_TO_LIST_OF_FILES) as file:
                result = [int(line.split(SPLIT)[1].strip()) for line in file]
            return DocumentSkipList(result)

        self.inverted_index = inverted_index
        assert ALL not in self.inverted_index
        self.inverted_index[ALL] = get_all_file_ids()

    @staticmethod
    def _intersect(t1: DocumentSkipList, t2: DocumentSkipList
                   ) -> DocumentSkipList:
        """
        AND operation

        Algorithm:
        While the end of one of the document lists is not found:
            1. while t1[i] == t2[j] -> append to results
            2. while t1[i] > t2[j] -> i = succ(i)
            3. while t1[i] < t2[j] -> j = succ(j)

        :param t1: list of document ids where the first token is present
        :param t2: list of document ids where the second token is present
        :return: list of documents where both tokens are present
        """

        def is_not_end() -> bool:
            return i < len(t1) and j < len(t2)

        result = DocumentSkipList()
        i, j = 0, 0
        while is_not_end():
            while is_not_end() and t1[i] == t2[j]:
                result.add(t1[i].id)
                i += 1
                j += 1
            if j < len(t2):
                i = t1.skip_until_ge(i, t2[j])
            if i < len(t1):
                j = t2.skip_until_ge(j, t1[i])
        return result

    @staticmethod
    def _concatenate(t1: DocumentSkipList, t2: DocumentSkipList
                     ) -> DocumentSkipList:
        """
        AND operation

        Algorithm:
        While the end of one of the document lists is not found:
            1. while t1[i] == t2[j] -> append to results
            2. while t1[i] > t2[j] -> i = succ(i)
            3. append to result list values in t1 which are less then
                current value in t2
            4. while t1[i] < t2[j] -> j = succ(j)
            5. append to result list values in t2 which are less then
                a current value in t1

        :param t1: list of document ids where the first token is present
        :param t2: list of document ids where the second token is present
        :return: list of documents where either one of tokens is present present
        """

        def is_not_end() -> bool:
            return i < len(t1) and j < len(t2)

        result = DocumentSkipList()
        i, j = 0, 0
        while is_not_end():
            while is_not_end() and t1[i] == t2[j]:
                result.add(t1[i].id)
                i += 1
                j += 1
            if j < len(t2):
                next_i = t1.skip_until_ge(i, t2[j])
                result.add_list([node.id for node in t1[i:next_i]])
                i = next_i
            if i < len(t1):
                next_j = t2.skip_until_ge(j, t1[i])
                result.add_list([node.id for node in t2[j:next_j]])
                j = next_j
        return result

    def exclude(self, document_list: DocumentSkipList, args
                ) -> DocumentSkipList:
        documents_to_exclude = [node.id for node in document_list]
        result = DocumentSkipList()
        for doc_id in self.inverted_index[ALL]:
            if doc_id.id not in documents_to_exclude:
                result.add(doc_id.id)
        return result

    # idea: implement binary search in inverted index
    def get_ids(self, token) -> Optional[DocumentSkipList]:
        try:
            return self.inverted_index[token]
        except KeyError:
            pass

    def process_operation(self, operator: str, t1: DocumentSkipList,
                          t2: DocumentSkipList = None) -> DocumentSkipList:
        try:
            options = {
                OPERATION_CODES.AND:
                    self._intersect,
                OPERATION_CODES.OR:
                    self._concatenate,
                OPERATION_CODES.NOT: self.exclude
            }
            return options[operator](t1, t2)
        except KeyError:
            raise NotImplementedError(
                f'Operator "{operator}" is not supported')
        except TypeError as e:
            print(operator, t1, t2)
            raise TypeError(e)

    def _search_not_null_query(self, notation: list):
        def pop_last_result() -> DocumentSkipList:
            """
            if an item on the top of the stack is a token, find a list of
            :return: skip list of document ids
            """
            last_token = stack.pop()
            if isinstance(last_token, str):
                last_token = self.get_ids(last_token)
            return last_token

        def process_operation_and_put_result_to_stack():
            if token == OPERATION_CODES.NOT:
                last_result = pop_last_result()
                stack.append(self.process_operation(token, last_result))
            else:
                t1, t2 = pop_last_result(), pop_last_result()
                if t1 and t2:
                    stack.append(self.process_operation(token, t1, t2))
                elif t1:
                    stack.append(t1)
                elif t2:
                    stack.append(t2)

        tokenizer = Tokenizer()
        stack = list()
        for token in notation:
            if isinstance(token, OPERATION_CODES):
                process_operation_and_put_result_to_stack()
            else:
                result_token = tokenizer.tokenize(token)
                stack.append(result_token[0][1]) \
                    if result_token else stack.append(ALL)
        if len(stack) > 1:
            raise AttributeError(f'"{notation}" is incorrect or there is '
                                 f'a bug in the algorythm implementation.\n'
                                 f'Stack is not empty at the end: f{stack}')
        return pop_last_result().to_list()

    def search(self, notation: list) -> list:
        if len(notation) == 0 or notation is None:
            return self.inverted_index[ALL].to_list()
        return self._search_not_null_query(notation)
