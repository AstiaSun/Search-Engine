import os

import pytest

from common.constants import PATH_TO_RESULT_DIR
from dictionary.strip_dictionary import StripDictionary, StripBlockDictionary, \
    FrontPackDictionary


@pytest.mark.parametrize('method_obj', [StripDictionary, StripBlockDictionary,
                                        FrontPackDictionary])
def test_strip_dictionary(method_obj):
    dict_object = method_obj()
    dict_object.build(os.path.join(PATH_TO_RESULT_DIR, 'test', 'dict'))
    assert dict_object.get_token(0) == 'cann'
    assert dict_object.get_token(1) == 'canni'
    assert dict_object.get_token(-1) == 'canon'
    assert dict_object.get_documents(2) == ['0', '1', '4', '7', '8']
    assert dict_object.get_frequency(2) == 39
