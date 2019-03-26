import pytest

from bool_search import load_inverted_skip_index, build_notation, \
    SearchBTree, SearchDictionary


@pytest.fixture
def inverted_index() -> SearchDictionary:
    yield load_inverted_skip_index()


@pytest.fixture
def btree(inverted_index) -> SearchBTree:
    btree = SearchBTree()
    for key in inverted_index.inverted_index.keys():
        btree.put(key)
    yield btree


@pytest.skip
@pytest.mark.parametrize('query, expected_documents',
                         [('', [0, 1, 2, 4, 5, 6, 7, 8, 10, 11]),
                          ('and', [0, 1, 2, 4, 5, 6, 7, 8, 10, 11]),
                          ('or', [0, 1, 2, 4, 5, 6, 7, 8, 10, 11]),
                          ('-', [0, 1, 2, 4, 5, 6, 7, 8, 10, 11]),
                          ('yon yonder', [5, 10, 11]),
                          ('yon AND yonder', [5, 10, 11]),
                          ('yon OR yonder', [0, 2, 5, 8, 10, 11]),
                          ('yon -yonder', [0])])
def test_search(inverted_index: SearchDictionary,
                query: str, expected_documents: list):
    notation = build_notation(query)
    actual_documents = inverted_index.search(notation)
    assert actual_documents == expected_documents, \
        f'Expected: {expected_documents}\nActual:{actual_documents}'


@pytest.mark.parametrize('pattern', ['yok', 'yokefellow'])
def test_btree_search(btree, pattern):
    results = btree.get(pattern)
    print(f'Search query = "{pattern}"\nResult:\n')
    print('\n'.join(results))
