import pathlib
from queue import Queue
from typing import BinaryIO

import PyPDF2

from dictionary.exceptions import NotSupportedExtensionException

CHUNK_SIZE = 40 * 1024


class FileReader(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        pass

    def read_chunk(self) -> str:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class PlainTextReader(FileReader):
    def __init__(self, file_path):
        super(PlainTextReader, self).__init__(file_path)
        self.file = None

    def __enter__(self) -> FileReader:
        super(PlainTextReader, self).__enter__()
        self.file = open(self.file_path)
        return self

    def read_chunk(self) -> str:
        return self.file.read(CHUNK_SIZE)

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PlainTextReader, self).__exit__(exc_type, exc_val, exc_tb)
        if self.file:
            self.file.close()


class PdfReader(FileReader):
    page: str
    file: BinaryIO
    file_reader: PyPDF2.PdfFileReader

    def __init__(self, file_path):
        super(PdfReader, self).__init__(file_path)
        self.curr_page_num = 0
        self.chunks = Queue()

    def __enter__(self) -> FileReader:
        super(PdfReader, self).__enter__()
        self.file = open(self.file_path, 'rb')
        self.file_reader = PyPDF2.PdfFileReader(self.file)
        self.page = ''
        return self

    def _is_eof(self):
        return self.file_reader.getNumPages() <= self.curr_page_num

    def _read_page(self):
        page = ''
        while not page:
            if not self._is_eof():
                current_page = self.file_reader.getPage(self.curr_page_num)
                self.curr_page_num += 1
                page = current_page.extractText()
            else:
                break
        return page

    def _split_into_chunks_and_put_into_queue(self):
        """
        Split page into chunks with size of CHUNK_SIZE. If the last
        chunk is smaller then this size, it is saved in 'page' variable.
        If the end of file is reached the last chunk of page is put
        into the queue.
        """
        start_split_pos = min(CHUNK_SIZE, len(self.page))
        start_chunk_pos = 0
        for split_pos in range(start_split_pos, len(self.page), CHUNK_SIZE):
            page_slice = self.page[start_chunk_pos: split_pos]
            start_chunk_pos = split_pos
            self.chunks.put(page_slice)
        self.page = self.page[start_chunk_pos:]
        if self._is_eof():
            self.chunks.put(self.page)

    def _read_pages_and_put_chunks_to_queue(self):
        self.page += self._read_page()
        while len(self.page) < CHUNK_SIZE and not self._is_eof():
            self.page += self._read_page()
        self._split_into_chunks_and_put_into_queue()

    def read_chunk(self) -> str:
        """
        returns chunk from read from the file
        :return: chunk of document
        """
        if self.chunks.empty():
            self._read_pages_and_put_chunks_to_queue()
        return self.chunks.get()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PdfReader, self).__exit__(exc_type, exc_val, exc_tb)
        if self.file and not self.file.closed:
            self.file.close()


def get_file_reader_by_extension(file_path: str) -> FileReader:
    """
    List of supported formats:
    - plain text (txt, no extension)
    - pdf
    - HTML
    :param file_path: Path to file
    :return:
    """
    suffixes = pathlib.Path(file_path).suffixes
    if not suffixes:
        raise NotSupportedExtensionException(suffixes)
    if suffixes[-1] == '.txt':
        return PlainTextReader(file_path)
    if suffixes[-1] == '.pdf':
        return PdfReader(file_path)
    raise NotSupportedExtensionException(suffixes[-1])
