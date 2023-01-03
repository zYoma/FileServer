
def download_result_1():
    return {'tmp/download/': ['archive.zip', 'file.txt']}


def download_result_3():
    return {'tmp/download/': ['archive.zip', 'test.pdf']}


def download_result_2():
    return {'tmp/download/': ['archive.zip'], 'tmp/download/tmp': [], 'tmp/download/tmp/test_user': [],
            'tmp/download/tmp/test_user/docs': [], 'tmp/download/tmp/test_user/docs/one': [],
            'tmp/download/tmp/test_user/docs/one/two': ['new.txt', 'test.pdf']}
