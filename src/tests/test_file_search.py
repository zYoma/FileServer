import pytest
from httpx import AsyncClient

from .conftest import base_url


@pytest.mark.parametrize('path, extension, order_by, result', [  # noqa
    ('', '', 'created_ad', ['file.txt', 'test.pdf', 'new.txt']),
    ('', '', 'size', ['new.txt', 'test.pdf', 'file.txt']),
    ('', 'pdf', 'size', ['test.pdf']),
    ('tmp/test_user/file.txt', '', 'size', ['file.txt']),
    ('tmp/test_user/file.txt', 'txt', 'name', ['file.txt']),
])
async def test_search_file(path, extension, order_by, result, test_app, token1, create_files):
    params = {
        "path": path,
        "extension": extension,
        "order_by": order_by,
    }
    async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token1}) as ac:
        response = await ac.get(test_app.url_path_for('search_files'), params=params)
    assert response.status_code == 200, "статус код ответа не верный"
    test_result = response.json()

    file_names = [i['name'] for i in test_result['matches']]
    assert file_names == result, "список полученных имен файлов не верный"
