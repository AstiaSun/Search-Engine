import pytest

from bool_search import load_inverted_skip_index, build_notation
from bool_search.search_dictionary import SearchDictionary


@pytest.fixture
def inverted_index() -> SearchDictionary:
    yield load_inverted_skip_index()


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
