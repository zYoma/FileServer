import pytest
from httpx import AsyncClient

from .conftest import base_url


@pytest.mark.parametrize('username, code', [  # noqa
    ('bad_name', 401),
    ('test_user', 200),
])
async def test_auth(username, code, test_app):
    async with AsyncClient(app=test_app, base_url=base_url) as ac:
        data = {
            "username": username,
            "password": 'string',
        }
        response = await ac.post(test_app.url_path_for('login_for_access_token'), data=data)
        test_result = response.json()
        assert response.status_code == code, "статус код ответа не верный"
        if response.status_code == 200:
            assert test_result["access_token"] is not None



@pytest.mark.parametrize('username, code', [  # noqa
    ('bad_name_@$', 422),
    ('test_user', 400),
    ('user', 201),
])
async def test_register(username, code, test_app):
    async with AsyncClient(app=test_app, base_url=base_url) as ac:
        data = {
            "username": username,
            "password": 'string',
        }
        response = await ac.post(test_app.url_path_for('register'), json=data)
        test_result = response.json()

        assert response.status_code == code, "статус код ответа не верный"
        if response.status_code == 201:
            assert test_result["username"] == 'user'


async def test_status(test_app, token1, token2, create_files):
    async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token1}) as ac:
        response = await ac.get(test_app.url_path_for('file_status'))

    assert response.status_code == 200, "статус код ответа не верный"
    test_result = response.json()
    assert len(str(test_result["folders"])) == 153, "размер ответа приведенного к строке не верный "

    async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token2}) as ac:
        response = await ac.get(test_app.url_path_for('file_status'))

    assert response.status_code == 200, "статус код ответа не верный"
    test_result = response.json()
    assert test_result["folders"] == []
