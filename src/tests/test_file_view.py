import pytest
from httpx import AsyncClient

from .conftest import base_url
from .mocks.file_view import file_view_result_1, file_view_result_2


@pytest.mark.parametrize('file_num, code, result', [  # noqa
    (0, 400, file_view_result_1()),
    (2, 200, file_view_result_2()),
])
async def test_get_file_list(file_num, code, result, test_app, token1, create_files):
    file_id = create_files[file_num]["id"]
    async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token1}) as ac:
        response = await ac.get(test_app.url_path_for('file_view', file_id=file_id))
        test_result = response.json()
        assert response.status_code == code, "статус код ответа не верный"
        if response.status_code != 200:

            assert test_result == result, "полученная ошибка не верная"
            return
        assert test_result["content"] == result, "содержимое файла не верное"
