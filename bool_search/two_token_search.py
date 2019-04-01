from bool_search.query_parser import OPERATIONS
from bool_search.skip_list_search import SearchDictionary
from common import read_file_dictionary


class PhraseSearchDictionary(SearchDictionary):
    def search(self, query: list) -> list:
        """
        Search in the two word dictionary
        :param query: phrases/words to search
        :return: list of documents
        """
        last_token = None
        result = None
        for token in query:
            if last_token is not None:
                current_result = self.get_ids(f'{last_token} {token}')
                result = current_result if result is None \
                    else super()._intersect(result, current_result)
            last_token = token
        return result.to_list()


class SearchCoordinatedDictionary(SearchDictionary):
    @staticmethod
    def _get_coordinate_index(query: list, result_documents: list) -> dict:
        """
        builds query coordinated index
        :param query: search query, already processed to notation or raw text
        :return: dictionary of token intersections with the next structure:
        {
            token1: {<doc_id>: [pos1, pos2, ..posn], <doc2>: [..]}
        }
        """
        tokens = {token: {} for token in query if query not in OPERATIONS.ALL}
        coordinated_index = {token: [] for token in tokens}
        for document in result_documents:
            dictionary = read_file_dictionary(str(document))
            for token in tokens:
                coordinated_index[token][document] = dictionary[token]
        return coordinated_index

    def search(self, query: list, max_distance: int = 2) -> list:
        """
        :param query: search query
        :param max_distance: maximum amount of characters between two words
        :return: list of documents with start phrase positions sorted from
        the most appropriate (the longest match) to the least appropriate
        """
        result_documents = super().search(query)
        query = list(filter(lambda x: x not in OPERATIONS.ALL, query))
        coordinate_index = self._get_coordinate_index(query, result_documents)

        longest_results = list()
        for doc_id, positions in coordinate_index[query[0]]:
            local_results = {pos: 0 for pos in positions}
            for start_position in positions:
                end_position = start_position + len(query[0])
                for i in range(1, len(query)):
                    position = 0
                    for position in coordinate_index[query[i]][doc_id]:
                        if position < end_position:
                            continue
                    if end_position < position < end_position + max_distance:
                        local_results[start_position] += 1
                else:
                    break
            longest_position = None, 0
            for pos, length in local_results.items():
                if longest_position[0] is None:
                    longest_position = (pos, length)
                if length > longest_position[1]:
                    longest_position = pos, length
            longest_results.append(
                (doc_id, longest_position[0], longest_position[1]))
        return longest_results
