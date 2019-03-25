import os

from common import constants


def read_positions_in_file(
        file_id: str, token: str,
        file_path: str = constants.PATH_TO_RESULT_DIR) -> list:
    with open(os.path.join(file_path, file_id)) as file:
        line = file.readline().strip()
        while line and line.split(constants.SPLIT) != token:
            line = file.readline().strip()
        if not line:
            return list()
        positions = line.split(constants.SPLIT)[1]
        return [int(pos) for pos in positions]


def read_file_dictionary(
        file_id: str,
        file_path: str = constants.PATH_TO_RESULT_DIR) -> dict:
    result = dict()
    with open(os.path.join(file_path, file_id)) as file:
        line = file.readline().strip()
        while line:
            token, positions = line.split(constants.SPLIT)
            result[token] = [int(pos) for pos in positions.split(',')]
            line = file.readline().strip()
    return result
