from enum import Enum

from sortedcontainers import SortedList

from bool_search import SearchBTree
from bool_search.skip_list_search import SearchDictionary, DocumentSkipList, \
    OPERATION_CODES, ALL


class WildcardSearch(SearchDictionary):
    MODE = Enum('MODE', 'TREE_GRAM BTREE')

    def __init__(self, inverted_index: dict):
        super().__init__(inverted_index)
        self.straight_btree = SearchBTree()
        self.inverted_btree = SearchBTree()
        for token in self.inverted_index.keys():
            self.inverted_btree.put(token[::-1])
            self.straight_btree.put(token)

    def _search_in_btrees(self, token: str) -> list:
        sub_token = token
        wildcard_pos = -1
        results = SortedList()
        while sub_token[wildcard_pos + 1:]:
            wildcard_pos = sub_token.index('*')
            docs = self.straight_btree.get(sub_token[:wildcard_pos])
            results.update(docs)
            sub_token = sub_token[wildcard_pos + 1:]
        return list(results)

    def _k_gram_search(self, token: str, k: int = 3):
        pass

    def _search_with_wildcards(self, token: str, algorithm: MODE = MODE.BTREE
                               ) -> list:
        search = {
            self.MODE.BTREE: self._search_in_btrees,
            self.MODE.THREE_GRAM: self._k_gram_search
        }
        return search[algorithm](token)

    def search(self, notation: list) -> list:
        """
        Search in the straight and inverted b-trees of search in the tokens
        :param notation: query to search where some token contain a wildcard
        :return: a list of documents which match the query
        """

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

        if len(notation) == 0 or notation is None:
            return self.inverted_index[ALL].to_list()
        if len(notation) == 1 and notation[0] not in OPERATION_CODES:
            return self._search_with_wildcards(notation[0])
        stack = list()
        for token in notation:
            if isinstance(token, OPERATION_CODES):
                process_operation_and_put_result_to_stack()
            else:
                if '*' in token:
                    tokens = self._search_with_wildcards(token)
                    query = tokens + [OPERATION_CODES.AND
                                      for _ in range(len(tokens) - 1)]
                    stack.append(self.search(query))
                else:
                    stack.append(token)
        if len(stack) > 1:
            raise AttributeError(f'"{notation}" is incorrect or there is '
                                 f'a bug in the algorithm implementation.\n'
                                 f'Stack is not empty at the end: f{stack}')
        return pop_last_result().to_list()
