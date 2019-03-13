import re
import unicodedata
from typing import Tuple

import nltk
from nltk.corpus import stopwords
from nltk.tokenize.toktok import ToktokTokenizer

CONTRACTION_MAP = {
    "ain't": "is not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'd've": "he would have",
    "he'll": "he will",
    "he'll've": "he he will have",
    "he's": "he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "I'd": "I would",
    "I'd've": "I would have",
    "I'll": "I will",
    "I'll've": "I will have",
    "I'm": "I am",
    "I've": "I have",
    "i'd": "i would",
    "i'd've": "i would have",
    "i'll": "i will",
    "i'll've": "i will have",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "it will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she would",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so as",
    "that'd": "that would",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there would",
    "there'd've": "there would have",
    "there's": "there is",
    "they'd": "they would",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you would",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have"
}


class Tokenizer:
    tokenizer = ToktokTokenizer()
    stopwords_list = stopwords.words('english')

    def __init__(self):
        self.stopwords_list.remove('no')
        self.stopwords_list.remove('not')

    @staticmethod
    def _remove_accented_chars(text: str) -> str:
        """
        converts characters like é to e
        :param text: text to process
        :return: converted text
        """
        text = unicodedata.normalize('NFKD', text) \
            .encode('ascii', 'ignore') \
            .decode('utf-8', 'ignore')
        return text

    @staticmethod
    def _expand_contractions(
            text: str,
            contraction_mapping: dict = None) -> str:
        """
        Language contain contractions like don't, isn't, we have to
        rearrange them into do not, is not
        :param text: words to process
        :param contraction_mapping: rules how to expand the words
        :return: text with expanded contractions
        """

        def expand_match(contraction):
            match = contraction.group(0)
            first_char = match[0]
            expanded_contraction = contraction_mapping.get(match) \
                if contraction_mapping.get(match) \
                else contraction_mapping.get(match.lower())
            expanded_contraction = first_char + expanded_contraction[1:]
            return expanded_contraction

        if contraction_mapping is None:
            contraction_mapping = CONTRACTION_MAP
        contractions_pattern = re.compile(
            '({})'.format('|'.join(contraction_mapping.keys())),
            flags=re.IGNORECASE | re.DOTALL)
        expanded_text = contractions_pattern.sub(expand_match, text)
        expanded_text = re.sub("'", "", expanded_text)
        return expanded_text

    @staticmethod
    def _remove_special_characters(text: str, remove_digits=False) -> str:
        """removes all special characters from the text"""
        pattern = r'[^a-zA-z0-9\s]' if not remove_digits else r'[^a-zA-z\s]'
        text = re.sub(pattern, '', text)
        return text

    @staticmethod
    def _stemming(text: str) -> str:
        # possible algorithms: Lancaster Stemmer, Snowball Stemmer
        ps = nltk.porter.PorterStemmer()
        return ' '.join([ps.stem(word) for word in text.split()])

    @staticmethod
    def _lemmatization(text: str) -> str:
        lemmatizer = nltk.stem.WordNetLemmatizer()
        return lemmatizer.lemmatize(text)

    def _remove_stopwords(self, text: str, is_lower_case=False) -> str:
        tokens = self.tokenizer.tokenize(text)
        if is_lower_case:
            filtered_tokens = [token for token in tokens if
                               token not in self.stopwords_list]
        else:
            filtered_tokens = [token for token in tokens if
                               token.lower() not in self.stopwords_list]
        filtered_text = ' '.join(filtered_tokens)
        return filtered_text

    @staticmethod
    def _get_token_with_index(text: str) -> Tuple[int, str]:
        for m in re.finditer(r'\S+', text):
            yield m.start(), m.group()

    def tokenize(self, text: str,
                 remove_accented_charactes: bool = True,
                 expand_contractions: bool = True,
                 remove_stopwords: bool = True,
                 remove_special_characters: bool = True,
                 do_lemmatization: bool = True,
                 do_stemming: bool = True) -> list:
        normalized_tokens = list()
        for index, token in self._get_token_with_index(text):
            if remove_accented_charactes:
                token = self._remove_accented_chars(token)
            if expand_contractions:
                token = self._expand_contractions(token)
            if remove_stopwords:
                token = self._remove_stopwords(token).strip()
            if remove_special_characters:
                token = self._remove_special_characters(token)
            if do_lemmatization:
                token = self._lemmatization(token)
            if do_stemming:
                token = self._stemming(token)
            if token:
                token = token.strip()
                normalized_tokens.append((index, re.sub(' +', ' ', token)))
        return normalized_tokens
