def read_next_line(path_to_file: str) -> str:
    with open(path_to_file, encoding='utf-8') as file:
        yield file.readline()
