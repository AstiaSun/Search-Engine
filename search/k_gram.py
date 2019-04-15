from sortedcontainers import SortedDict


class PermutationIndex:
    EOW = '$'

    def __init__(self, k: int = 3):
        self.permutation_index = SortedDict()
        self.k = k

    def get_permutations(self, tokens: list):
        for token in tokens:
            token = token + self.EOW
            shifts = list()
            while token[0] != self.EOW:
                shifts.append(token)
                token = token[1:] + token[0]
            self.permutation_index[token[1:]] = shifts

    def search(self, token_part):
        pass
