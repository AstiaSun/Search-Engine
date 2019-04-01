from dataclasses import dataclass, field
from typing import Union, Optional

from sortedcontainers import SortedList


class IncorrectNodeParameters(Exception):
    def __init__(self, key_number, children_numder):
        super().__init__(f'Tried to set a node with {key_number} '
                         f'keys and {children_numder} children')


@dataclass
class Node:
    """
    Represents node in BTree
    """
    keys: SortedList = field(default_factory=SortedList)
    children: list = field(default_factory=list)
    parent: Optional = None

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def set_keys(self, keys: list):
        self.keys = SortedList(keys)

    def set_children(self, children: list):
        self.children = sorted(children, key=lambda x: x.keys[0])


def create_new_node(parent: Optional[Node],
                    keys: Optional[Union[list, SortedList]],
                    children: Optional[list]) -> Node:
    node = Node()
    node.parent = parent
    if keys is not Node:
        node.set_keys(keys)
    if children is not None:
        if len(keys) != len(children) - 1:
            # TODO: a problem with list where keys are not unique
            raise IncorrectNodeParameters(len(keys), len(children))
        for child in children:
            child.parent = node
        node.set_children(children)
    return node


def get_tokens_in_children(query: str, start_node: Node) -> list:
    def is_current_node_satisfies_token() -> bool:
        last_key = current_node.keys[i]
        return len(last_key) >= len(query) and last_key.startswith(query)

    result = list()
    current_node = start_node
    i = 0
    while i < len(current_node.keys) and is_current_node_satisfies_token():
        result.append(current_node.keys[i])
        if not current_node.is_leaf():
            result.extend(
                get_tokens_in_children(query, current_node.children[i]))
        i += 1
    if i == len(current_node.keys) and not current_node.is_leaf():
        result.extend(get_tokens_in_children(query, current_node.children[i]))
    return result


class SearchBTree:
    """
    Represents BTree which implements search in word dictionary.
    Search can be done by the start of a word.
    """
    order: int = 6

    def __init__(self, order: int = 6):
        """
        :param order: Knuth order of the btree - a maximum amount of
        children the node can have. By default the value is equal to 6 as
        it is an optimum order for dictionaries with about 5-6 thousands
        of tokens.
        """
        self.root = Node()
        self.order = order

    def get_node(self, token: str, startswith: bool = True, leaf: bool = False
                 ) -> Optional[Node]:
        """
        Find a first key which satisfies the search query and return the
        key with appropriate children in a range of a btree
        :param token: token or start of a token to search for
        :param startswith: search token starts with the requested pattern
        :param leaf: is only a leaf is searched
        :return: <key value, list of appropriate children> if any
        result is found
        """

        def is_current_node_satisfies_token() -> bool:
            last_key = current_node.keys[max(0, i - 1)]
            return len(last_key) >= len(token) and last_key.startswith(token)

        current_node = self.root
        if len(self.root.keys) == 0:
            return
        while not current_node.is_leaf():
            i = 0
            while i < len(current_node.keys) and current_node.keys[i] < token:
                i += 1
            if not leaf and is_current_node_satisfies_token():
                return current_node
            current_node = current_node.children[i]
        return current_node \
            if not startswith or is_current_node_satisfies_token() \
            else None

    def get(self, token) -> list:
        """
        returns a list of tokens which starts with a provided character
        sequence
        :param token: character sequence of a token to compare with
        :return:
        """
        search_node = self.get_node(token)
        if search_node is None:
            return list()
        # search tokens by pattern in children
        return get_tokens_in_children(token, search_node)

    def _put(self, node: Node, value: str, children: Optional[list] = None):
        node.keys.add(value)
        if children is not None:
            node.set_children(node.children + children)
        if len(node.keys) >= self.order:
            median_index = round(len(node.keys) / 2)
            left_child = create_new_node(
                parent=node.parent,
                keys=node.keys[:median_index],
                children=None if node.is_leaf()
                else node.children[:median_index + 1])
            right_child = create_new_node(
                parent=node.parent,
                keys=node.keys[median_index + 1:],
                children=None if node.is_leaf()
                else node.children[median_index + 1:])
            if node.parent is None:
                self.root = create_new_node(
                    parent=None,
                    keys=node.keys[median_index:median_index + 1],
                    children=[left_child, right_child])
            else:
                node.parent.children.remove(node)
                self._put(node.parent, node.keys[median_index],
                          [left_child, right_child])

    def put(self, value: str):
        """
        All insertions start at a leaf node. To insert a new element,
        search the tree to find the leaf node where the new element
        should be added. Insert the new element into that node with
        the following steps:

        1. If the node contains fewer than the maximum allowed number
        of elements, then there is room for the new element. Insert the
        new element in the node, keeping the node's elements ordered.
        2. Otherwise the node is full, evenly split it into two nodes so:
            a) A single median is chosen from among the leaf's elements
            and the new element.
            b) Values less than the median are put in the new left node
            and values greater than the median are put in the new right
            node, with the median acting as a separation value.
            c) The separation value is inserted in the node's parent,
            which may cause it to be split, and so on. If the node has
            no parent (i.e., the node was the root), create a new root
            above this node (increasing the height of the tree).
        :param value:
        :return:
        """
        node = self.get_node(token=value, startswith=False, leaf=True)
        if node is None:
            self.root = create_new_node(None, [value], None)
        else:
            self._put(node, value)
