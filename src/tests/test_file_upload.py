import os
from unittest.mock import PropertyMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from db.models.file import File
from db.models.revision import Revision
from db.sqlalchemy.asyncpg import make_sessionmaker, session

from .conftest import base_url
from .mocks.file_upload import (upload_result_1, upload_result_2,
                                upload_result_3, upload_result_4,
                                upload_result_5, upload_result_6)


@pytest.mark.parametrize('path, file, code, result', [  # noqa
    ('file.txt', 'tests/mocks/test.jpg', 201, upload_result_1()),
    ('file.txt', 'tests/mocks/test.jpg', 201, upload_result_1()),
    ('/', 'tests/mocks/test.pdf', 201, upload_result_6()),
    ('/file.txt', 'tests/mocks/test.jpg', 201, upload_result_1()),
    ('/file', 'tests/mocks/test.pdf', 201, upload_result_2()),
    ('docs/one/two', 'tests/mocks/test.txt', 201, upload_result_3()),
    ('docs/one/two/new.txt', 'tests/mocks/test.txt', 201, upload_result_4()),
    ('/file', 'tests/mocks/big_file.jpg', 413, upload_result_5()),
])
async def test_upload(path, file, code, result, test_app, token1, engine, make_static_dir):
    params = {'path': path}
    files = {'file': open(file, "rb")}
    with patch(
            "services.file.FileManager.base_dir", new_callable=PropertyMock, return_value='tmp/'
    ):
        async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token1}) as ac:
            response = await ac.post(test_app.url_path_for('upload_file'), params=params, files=files)

    test_result = response.json()
    assert response.status_code == code, "статус код ответа не верный"
    if response.status_code != 201:
        assert test_result == result, "ответ в случае ошибки не верный"
        return

    file_id = test_result["id"]
    directory_id = test_result["directory_id"]
    user_id = test_result["user_id"]

    async with session(make_sessionmaker(engine)) as s:
        query = select(File).where(File.id == file_id)
        r = await s.execute(query)
        obj = r.scalars().first()
        assert obj is not None, "в БД не создан file"
        assert str(obj.directory_id) == directory_id, "директория файла не создана или указана не верно"
        assert str(obj.user_id) == user_id, "у файла указан не верный пользователь"

    async with session(make_sessionmaker(engine)) as s:
        query = select(Revision).where(Revision.file_id == file_id)
        r = await s.execute(query)
        obj = r.scalars().first()
        assert obj is not None, "в БД для файла не создана ревизия"

    assert test_result["name"] == result["name"], "имя файла сгенерировано не верно"
    assert test_result["path"] == result["path"], "путь до файла не верный"
    assert test_result["size"] == result["size"], "размер файла не верный"

    files_in_directories = {root: files for root, _, files in os.walk(make_static_dir)}
    assert files_in_directories == result["files_in_directories"], "структура созданных файлов на диске не верная"
