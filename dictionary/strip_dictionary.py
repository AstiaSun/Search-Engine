from bitarray import bitarray

from common.constants import PATH_TO_DICT, SPLIT, DIVIDER


def encode_gamma_code(n):
    if int(n) < 2:
        return bitarray(n), bitarray('')
    binary_n = format(int(n), 'b')
    binary_offset = binary_n[1::]
    unary_length = bitarray([True for _ in range(len(binary_offset))]) + \
        bitarray([False])
    return bitarray(unary_length), bitarray(binary_offset)


def decode_gamma_code(unary_n, offset):
    def to_int(binary):
        i = 0
        for bit in binary:
            i = (i << 1) | bit
        return i

    if len(offset) == 0:
        return to_int(unary_n)
    i = len(unary_n) - 1
    while unary_n[i] == '1' and i > 0:
        i -= 1
    appendix = bitarray('1' * (len(unary_n) - i))
    appendix.extend(offset)
    return to_int(appendix)


def encode_list(items: list) -> list:
    result = list()
    for doc_id in items:
        result.append(encode_gamma_code(doc_id))
    return result


def decode_list(items: list) -> list:
    result = list()
    for unary_n, offset in items:
        result.append(str(decode_gamma_code(unary_n, offset)))
    return result


class StripDictionary:
    """
    Used in order to save in RAM big dictionaries. Tokens are saved
    in the strip and the dictionary stores pointer to the place in
    the strip where the token is saved.
    """

    def __init__(self):
        self.strip = ''
        self.dictionary = list()
        self.with_frequency = True

    def build(self, path_to_dict: str = PATH_TO_DICT,
              with_frequency: bool = True):
        self.with_frequency = with_frequency
        with open(path_to_dict) as file:
            for line in file.readlines():
                token_id, doc_ids_str = line.split(SPLIT)
                doc_ids = doc_ids_str.strip().split(',')
                doc_ids = encode_list(doc_ids)
                if self.with_frequency:
                    token_id, frequency = token_id.split(DIVIDER)
                    record = (int(frequency), doc_ids, len(self.strip))
                else:
                    record = (doc_ids, len(self.strip))
                self.strip += token_id
                self.dictionary.append(record)

    def get_token(self, i: int) -> str:
        start = self.dictionary[i][-1]
        if i == -1:
            return self.strip[start:]
        if i < len(self.dictionary):
            end = self.dictionary[i + 1][-1]
            return self.strip[start:end]
        else:
            return self.strip[start:]

    def get_frequency(self, i: int) -> int:
        if self.with_frequency:
            return self.dictionary[i][0]
        raise RuntimeError('Frequency is not stored in the dictionary')

    def get_documents(self, i: int) -> list:
        if self.with_frequency:
            return decode_list(self.dictionary[i][1])
        return decode_list(self.dictionary[i][0])


class StripBlockDictionary(StripDictionary):
    SKIP_RANGE = 5

    def build(self, path_to_dict: str = PATH_TO_DICT,
              with_frequency: bool = True):
        self.with_frequency = with_frequency
        with open(path_to_dict) as file:
            i = 0
            for line in file.readlines():
                token_id, doc_ids_str = line.split(SPLIT)
                doc_ids = doc_ids_str.strip().split(',')
                doc_ids = encode_list(doc_ids)
                if self.with_frequency:
                    token_id, frequency = token_id.split(DIVIDER)
                    record = [int(frequency), doc_ids]
                else:
                    record = [doc_ids]
                if i == 0:
                    record.append(len(self.strip))
                i = (i + 1) % 5
                self.strip += str(len(token_id)) + token_id
                self.dictionary.append(record)

    def get_token(self, i: int) -> str:
        def get_next_word_pos(start):
            curr_len = int(self.strip[start])
            return start + curr_len + 1

        record = self.dictionary[i]
        while i < 0:
            i += len(self.dictionary)
        curr_record = i
        empty_record_len = 2 if self.with_frequency else 1
        while curr_record > 0 and len(record) == empty_record_len:
            curr_record -= 1
            record = self.dictionary[curr_record]
        skipped_words = i - curr_record
        start_pos = self.dictionary[curr_record][empty_record_len]
        for _ in range(skipped_words):
            start_pos = get_next_word_pos(start_pos)
        token_len = int(self.strip[start_pos])
        end_pos = min(len(self.strip),
                      start_pos + token_len + 1)
        return self.strip[start_pos + 1:end_pos]


class FrontPackDictionary(StripDictionary):
    MIN_COMMON_LEN = 4

    def build(self, path_to_dict: str = PATH_TO_DICT,
              with_frequency: bool = True):
        """
        Finds common part in tokens, saves it and then only the ending
        of tokens is saved. Example: 8automat*a1$e2$ic3$ion
        :param path_to_dict: path to dictionary to compress
        :param with_frequency: if frequency has been recorded
        """

        def get_common(s1: str, s2: str) -> str:
            min_len = min(len(s1), len(s2))
            char_i = 0
            while char_i < min_len:
                if s1[char_i] != s2[char_i]:
                    break
                char_i += 1
            return s1[:char_i]

        self.with_frequency = with_frequency
        with open(path_to_dict) as file:
            token_common = ''
            for line in file.readlines():
                token_id, doc_ids_str = line.split(SPLIT)
                doc_ids = doc_ids_str.strip().split(',')
                doc_ids = encode_list(doc_ids)
                if self.with_frequency:
                    token_id, frequency = token_id.split(DIVIDER)
                    record = [int(frequency), doc_ids]
                else:
                    record = [doc_ids]
                common = get_common(token_common, token_id)
                if len(common) < self.MIN_COMMON_LEN <= len(token_id):
                    record.append(len(self.strip))
                    token_common = token_id[:self.MIN_COMMON_LEN]
                    self.strip += str(len(token_id)) + \
                                  token_id[:self.MIN_COMMON_LEN] + '*' + \
                                  token_id[self.MIN_COMMON_LEN:]
                else:
                    token_id_part = token_id[self.MIN_COMMON_LEN:]
                    self.strip += str(len(token_id_part)) + '$' + token_id_part
                self.dictionary.append(record)

    def get_token(self, i: int) -> str:
        def get_next_word_pos(start):
            # + 1 - length of special symbol
            curr_len = int(self.strip[start])
            return start + curr_len + 1 + 1

        record = self.dictionary[i]
        while i < 0:
            i += len(self.dictionary)
        curr_record = i
        empty_record_len = 2 if self.with_frequency else 1
        while curr_record > 0 and len(record) == empty_record_len:
            curr_record -= 1
            record = self.dictionary[curr_record]
        skipped_words = i - curr_record
        if skipped_words == 0:
            start_pos = record[empty_record_len]
            word_length = int(self.strip[start_pos])
            shift = start_pos + 1
            if word_length <= self.MIN_COMMON_LEN:
                return self.strip[shift: shift + word_length]
            asterisk_pos = shift + self.MIN_COMMON_LEN
            postfix_len = word_length - self.MIN_COMMON_LEN
            return self.strip[shift: self.MIN_COMMON_LEN] + \
                   self.strip[asterisk_pos + 1:asterisk_pos + 1 + postfix_len]
        start_pos = self.dictionary[curr_record][empty_record_len]
        for _ in range(skipped_words):
            start_pos = get_next_word_pos(start_pos)
        end_pos = min(len(self.strip), get_next_word_pos(start_pos))
        shift = record[empty_record_len] + 1
        return self.strip[shift: shift + self.MIN_COMMON_LEN] + \
               self.strip[start_pos + 2:end_pos]
