from enum import Enum

ZONES = Enum('ZONES', 'AUTHOR TITLE BODY')
weights = [1, 0, 0]


def train_weights():
    pass


def calculate_weight(token: str, query: list) -> float:
    pass


def fetch_postings_list(token: str) -> list:
    pass


def cosine_score(query: list):
    scores = dict()
    length = [0 for _ in range(len(query))]
    for token in query:
        weight = calculate_weight(token, query)
        postings = fetch_postings_list(token)
        for document, tf in postings:
            if document not in scores:
                scores[document] = 0
            scores[token] += weight * calculate_weight(token, document)
