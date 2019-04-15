import pytest

from search import load_inverted_skip_index, build_notation, \
    SearchBTree, SearchDictionary, WildcardSearch, load_inverted_list


@pytest.fixture
def inverted_index() -> dict:
    yield load_inverted_list()


@pytest.fixture
def search_skip_list_dictionary() -> SearchDictionary:
    yield load_inverted_skip_index()


@pytest.fixture
def btree(inverted_index) -> SearchBTree:
    btree = SearchBTree()
    for key in inverted_index.keys():
        btree.put(key)
    yield btree


@pytest.fixture()
def wildcard_search(inverted_index):
    yield WildcardSearch(inverted_index)


@pytest.mark.skip
@pytest.mark.parametrize('query, expected_documents',
                         [('', [0, 1, 2, 4, 5, 6, 7, 8, 10, 11]),
                          ('and', [0, 1, 2, 4, 5, 6, 7, 8, 10, 11]),
                          ('or', [0, 1, 2, 4, 5, 6, 7, 8, 10, 11]),
                          ('-', [0, 1, 2, 4, 5, 6, 7, 8, 10, 11]),
                          ('yon yonder', [5, 10, 11]),
                          ('yon AND yonder', [5, 10, 11]),
                          ('yon OR yonder', [0, 2, 5, 8, 10, 11]),
                          ('yon -yonder', [0])])
def test_search(search_skip_list_dictionary: SearchDictionary,
                query: str, expected_documents: list):
    notation = build_notation(query)
    actual_documents = inverted_index.search(notation)
    assert actual_documents == expected_documents, \
        f'Expected: {expected_documents}\nActual:{actual_documents}'


@pytest.mark.parametrize('pattern, expected_result', [
    ('yok', ['yokd', 'yoke', 'yokel', 'yokedevil', 'yokeelm', 'yokefellow']),
    ('yokefellow', ['yokefellow'])
])
def test_btree_build_and_search(btree, pattern, expected_result):
    results = btree.get(pattern)
    print(f'Search query = "{pattern}"\nResult:\n')
    print('\n'.join(results))
    assert sorted(expected_result) == sorted(results)


@pytest.mark.parametrize('pattern, expected_result', [
    ('yok*', ['yokd', 'yoke', 'yokel', 'yokedevil', 'yokeelm', 'yokefellow']),
    ('y*l', ['yokel', 'yokedevil'])
])
def test_search_with_pattern(wildcard_search, pattern, expected_result):
    results = wildcard_search.search([pattern])
    print(results)
