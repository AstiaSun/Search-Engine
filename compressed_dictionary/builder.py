from dataclasses import dataclass

from BTrees.OOBTree import OOBTree


@dataclass
class TokenInfo:
    frequency: int
    doc_id: int
    index: int


# TODO: search in btree
class CompressedDict:
    def __init__(self):
        self.strip: str = ''
        self.dictionary = list()
        self.search_tree = OOBTree()

    def add(self, token, frequency, doc_id):
        self.dictionary.append(TokenInfo(frequency, doc_id, len(self.strip)))
        self.strip += token


class CompressedIndex:
    def __init__(self):
        pass
