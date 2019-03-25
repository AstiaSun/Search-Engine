import os
from _queue import Empty
from multiprocessing import Queue, Event, Process, Pool
from threading import Thread

from sortedcontainers import SortedDict

from common.constants import PATH_TO_DICT, PATH_TO_RESULT_DIR, \
    PATH_TO_LIST_OF_FILES, BYTE, PATH_TO_DATA_DIR
from dictionary.decoder import get_file_reader_by_extension
from dictionary.exceptions import NotSupportedExtensionException
from dictionary.utils import get_list_of_files, write_doc_ids_to_file, \
    write_dictionary_to_file, write_token_list_to_file, \
    add_unfinished_part_from_prev_chunk, get_tokens_from_chunk

CHUNK_SIZE = 4 * BYTE

QUEUE_MAX_SIZE = 10000
QUEUE_MIN_SIZE = 10000

CHUNK_WORKERS_NUM = 8
TOKEN_WORKERS_NUM = 2

chunk_queue = Queue()
token_queue = Queue()

file_job_done = Event()
token_job_done = Queue(maxsize=CHUNK_WORKERS_NUM)

inverted_index = SortedDict()
lexicon = dict()


def retrieve_tokens(chunk_start, chunk) -> list:
    """
    Receives chunk from the queue. Than replace punctuation with
    spaces and retrieve tokens with their positions in text
    return: file_id - docID of the material of origin,
    tokens - list of tokens with positions in text
    """
    tokens = get_tokens_from_chunk(chunk, chunk_start)
    return tokens


def notify_on_finish() -> None:
    """Send an event that the worked has finished reading from queue"""
    token_job_done.put(0)
    print("Chunk process down")


def get_chunk_from_queue_and_process() -> bool:
    """
    Get retrieved tokens from received chunk and puts them into the
    queue
    :return: True - waiting foe the next chunk, False - queue is closed
    """
    try:
        file_id, chunk_start, chunk = chunk_queue.get(block=True, timeout=1)
        tokens = retrieve_tokens(chunk_start, chunk)
        token_queue.put((file_id, tokens))
    except Empty:
        if file_job_done.is_set():
            notify_on_finish()
            return False
    return True


def chunk_to_tokens_worker() -> None:
    """
    While queue is not empty during timeout, read chunks from queue
    and split it to tokens. Then put tokens into the queue and wait
    for next chunk.
    """
    while True:
        if not get_chunk_from_queue_and_process():
            return


def get_list_or_add_to_lists(file_id: int) -> dict:
    if file_id not in lexicon:
        lexicon[file_id] = SortedDict()
    return lexicon[file_id]


def reduce_tokens_to_lexicon() -> None:
    """
    Read parsed token with position in specified documents and map them
    into token dictionary and inverted list of word positions
    :return: token_dict - token dictionary,
    word_position_lists - inverted list of token positions in documents
    """

    def append_token_to_dict():
        if token not in inverted_index:
            inverted_index[token] = set()
        inverted_index[token].add(file_id)

    def append_token_to_list():
        if token not in curr_word_position_list:
            curr_word_position_list[token] = []
        curr_word_position_list[token].append(position)

    while True:
        try:
            file_id, tokens = token_queue.get(block=True, timeout=1)
            curr_word_position_list = \
                get_list_or_add_to_lists(file_id)

            for position, token in tokens:
                append_token_to_dict()
                append_token_to_list()

        except Empty:
            print("Failed to read from token queue")
            if token_job_done.full():
                print('Worker finished')
                return


def read_document_and_put_into_queue(file_path: str, file_id: int) -> None:
    """
    Read document chunk by chunk and put them into the queue
    :param file_path: Path to document which will be read
    :param file_id: generated docID of the document
    """
    chunk_start = 0
    unfinished_part = ''
    with get_file_reader_by_extension(file_path) as file:
        chunk = file.read_chunk()
        while chunk:
            actual_chunk, unfinished_part = \
                add_unfinished_part_from_prev_chunk(chunk, unfinished_part)
            chunk_queue.put((file_id, chunk_start, actual_chunk))

            chunk = file.read_chunk()
            chunk_start += len(actual_chunk) + 1
        if unfinished_part:
            chunk_queue.put((file_id, chunk_start, unfinished_part))


def read_document_if_extension_is_supported(file_path, file_id) -> bool:
    try:
        read_document_and_put_into_queue(file_path, file_id)
    except NotSupportedExtensionException as e:
        print(e.message)
        return False
    return True


def process_documents() -> None:
    """
    1. Discover file in the directory and give them a unique ID.
    2. Read each file if it is a document and the extension is
    supported by the parser. Put read parts into the queue to parse
    text into the tokens.
    3. Save document's IDs to file on disk
    """
    documents_with_id = dict()

    for file_id, file_name in get_list_of_files():
        file_path = os.path.join(PATH_TO_DATA_DIR, file_name)

        if not os.path.isfile(file_path):
            continue

        if read_document_if_extension_is_supported(file_path, file_id):
            documents_with_id[file_path] = file_id

    file_job_done.set()
    print('Documents are read')
    write_doc_ids_to_file(documents_with_id, PATH_TO_LIST_OF_FILES)


def main() -> None:
    """
    Algorithm:
    1. Producer reads documents -> puts data into the queue ->
        adds document to the dictionary <doc_id, file_name>
    2. First-layer consumers read the data queue -> tokenize the text
    -> put into reduce queue
    3. Reducers merge tokens into local lexicons -> put mini lexicons
    to reduce queue 2
    4. Global reducer reduces mini lexicons to global lexicon and when
    writes result into files.
    """
    producer = Process(target=process_documents)
    producer.start()
    chunk_workers = Pool(CHUNK_WORKERS_NUM)
    for _ in range(CHUNK_WORKERS_NUM):
        chunk_workers.apply_async(chunk_to_tokens_worker)

    threads = []
    for _ in range(TOKEN_WORKERS_NUM):
        t = Thread(target=reduce_tokens_to_lexicon)
        threads.append(t)
        t.start()

    [t.join() for t in threads]
    print('dictionary created')

    write_lexicon_process = \
        Process(target=write_dictionary_to_file,
                args=(inverted_index, PATH_TO_DICT, True))
    write_lexicon_process.start()

    for file_id, word_position_list in lexicon.items():
        path_to_result_file = \
            os.path.join(PATH_TO_RESULT_DIR, str(file_id))
        write_token_list_to_file(word_position_list, path_to_result_file)

# if __name__ == '__main__':
#    start_time = time.time()
#   main()
#    spent_time = time.time() - start_time
#    print(f'{spent_time} was elapsed')
