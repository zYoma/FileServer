import pytest
from httpx import AsyncClient

from .conftest import base_url


@pytest.mark.parametrize('path', [  # noqa
    ('tmp/test_user/docs/one/two/new.txt'),
    ('tmp/test_user/file.txt'),
    ('tmp/test_user/docs/one/two/test.pdf'),
])
async def test_revision_file(path, test_app, token1, create_files):
    params = {
        "path": path,
    }
    async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token1}) as ac:
        response = await ac.get(test_app.url_path_for('revision_files'), params=params)
    assert response.status_code == 200, "статус код ответа не верный"
    test_result = response.json()

    assert len(test_result) == 1, "количество результатов не верное"
    keys_name = [i for i in test_result[0]]
    file_ids = [v for i in create_files for k, v in i.items() if k == 'id']
    assert test_result[0]['id'] in file_ids, "id файла не верный"
    assert keys_name == ['id', 'name', 'created_ad', 'path', 'rev_id', 'hash', 'modified_at'], "список полей ответа не верный"
