from httpx import AsyncClient

from .conftest import base_url


async def test_get_file_list(test_app, token1, token2, create_files):
    async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token1}) as ac:
        response = await ac.get(test_app.url_path_for('get_list_file'))
        test_result = response.json()
        assert response.status_code == 200, "статус код ответа не верный"
        assert len(test_result) == 3, "количество файлов в ответе не верное"
    # для другого пользака
    async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token2}) as ac:
        response = await ac.get(test_app.url_path_for('get_list_file'))
        test_result = response.json()
        assert response.status_code == 200, "статус код ответа не верный"
        assert len(test_result) == 0, "количество файлов в ответе не верное"
