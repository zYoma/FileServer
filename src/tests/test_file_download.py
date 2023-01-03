import os
import zipfile
from unittest.mock import PropertyMock, patch

import pytest
from httpx import AsyncClient

from .conftest import base_url
from .mocks.file_download import (download_result_1, download_result_2,
                                  download_result_3)


@pytest.mark.parametrize('path, code, result', [  # noqa
    ('file.txt', 404, ""),
    ('tmp/test_user/file.txt', 200, download_result_1()),
    ('id', 200, download_result_3()),
    ('tmp/test_user/docs/one/two/', 200, download_result_2()),
])
async def test_download_file(path, code, result, test_app, token1, create_files):
    if path == 'id':
        path = create_files[1]['id']

    with patch(
            "services.file.DownloadFileManager.base_dir", new_callable=PropertyMock, return_value='tmp/'
    ):
        async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token1}) as ac:
            response = await ac.get(test_app.url_path_for('download_file'), params={"path": path})
        assert response.status_code == code, "статус код ответа не верный"
        if response.status_code != 200:
            test_result = response.json()
            assert test_result == {'detail': {'code': 'NOT_FOUND', 'error': '', 'message': 'Not Found'}}
            return

        assert dict(response.headers) == {
            'content-disposition': 'attachment;filename=archive.zip',
            'content-type': 'application/x-zip-compressed',
        }, "заголовок ответа не верный"

        file_data = bytearray()
        for bytes in response.iter_bytes():
            file_data += bytes

        download_dir = 'tmp/download/'
        zip_path = 'tmp/download/archive.zip'
        os.makedirs(download_dir, exist_ok=True)

        with open(zip_path, 'wb') as f:
            f.write(file_data)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_dir)

        files_in_directories = {root: files for root, _, files in os.walk(download_dir)}
        assert files_in_directories == result, "количество файлов в ответе не верное"
