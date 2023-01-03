from config import settings


def upload_result_1():
    return {
        "name": "file.txt",
        "size": 353753,
        "path": "tmp/test_user/file.txt",
        "files_in_directories": {'tmp/': [], 'tmp/test_user': ['file.txt']},
    }


def upload_result_2():
    return {
        "name": "test.pdf",
        "size": 306207,
        "path": "tmp/test_user/file/test.pdf",
        "files_in_directories": {'tmp/': [], 'tmp/test_user': [], 'tmp/test_user/file': ['test.pdf']},
    }


def upload_result_3():
    return {
        "name": "test.txt",
        "size": 176,
        "path": "tmp/test_user/docs/one/two/test.txt",
        "files_in_directories": {'tmp/': [], 'tmp/test_user': [], 'tmp/test_user/docs': [],
                                 'tmp/test_user/docs/one': [], 'tmp/test_user/docs/one/two': ['test.txt']},
    }


def upload_result_4():
    return {
        "name": "new.txt",
        "size": 176,
        "path": "tmp/test_user/docs/one/two/new.txt",
        "files_in_directories": {'tmp/': [], 'tmp/test_user': [], 'tmp/test_user/docs': [],
                                 'tmp/test_user/docs/one': [], 'tmp/test_user/docs/one/two': ['new.txt']},
    }


def upload_result_5():
    return {'detail': {'code': 'VALIDATION_ERROR', 'error': '',
                       'message': f'Размер файла не должен превышать {settings.MAX_FILE_SIZE_KB} kb'}}


def upload_result_6():
    return {
        "name": "test.pdf",
        "size": 306207,
        "path": "tmp/test_user/test.pdf",
        "files_in_directories": {'tmp/': [], 'tmp/test_user': ['test.pdf']},
    }
