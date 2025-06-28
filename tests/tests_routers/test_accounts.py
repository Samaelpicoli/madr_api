from http import HTTPStatus

from madr.schemas.account_schema import AccountPublic


def test_create_account_should_return_created_account(client):
    """
    Testa se o endpoint /accounts/ cria uma conta e retorna os
    dados da conta criado.

    Verifica se a resposta da API contém o status code 201 (Created) e
    se o corpo da resposta contém os dados da conta criado, incluindo
    o ID gerado automaticamente.
    """
    account_data = {
        'username': 'testuser',
        'email': 'teste@teste.com',
        'password': 'testpassword',
    }
    response = client.post('/accounts/', json=account_data)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'testuser',
        'email': 'teste@teste.com',
    }


def test_create_account_should_return_409_error_when_account_already_exists(
    client, account
):
    """
    Testa se o endpoint /accounts/ retorna erro 409 quando
    a conta já existe.

    Verifica se a resposta da API contém o status code 409 (Conflict)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o nome de conta já existe.
    """
    response = client.post(
        '/accounts/',
        json={
            'username': account.username,
            'email': 'test@test.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_account_should_return_409_error_when_email_already_exists(
    client, account
):
    """
    Testa se o endpoint /accounts/ retorna erro 409 quando
    o email já existe.

    Verifica se a resposta da API contém o status code 409 (Conflict)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o email da conta já existe.
    """
    response = client.post(
        '/accounts/',
        json={
            'username': 'sama',
            'email': account.email,
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_read_accounts_should_return_account_list(client, account, token):
    """
    Testa se o endpoint /accounts/ retorna uma lista de contas.
    Utiliza a fixture 'account' para criar uma conta no banco de dados.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados da conta criado.
    """
    account_schema = AccountPublic.model_validate(account).model_dump()
    response = client.get(
        '/accounts/', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'accounts': [account_schema]}


def test_update_account_should_return_update_account(client, account, token):
    """
    Testa se o endpoint /accounts/{account_id} atualiza os dados de uma conta
    e retorna os dados atualizados.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados da conta atualizados,
    incluindo o novo nome de usuário e email.
    """
    response = client.put(
        f'/accounts/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'updateduser',
            'email': 'update@update.com',
            'password': 'updatepassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'updateduser',
        'email': 'update@update.com',
    }


def test_update_account_should_return_409_error_when_account_already(
    client, account, other_account, token
):
    """
    Testa se o endpoint /accounts/{account_id} retorna erro 409 quando
    a conta já existe.

    Verifica se a resposta da API contém o status code 409 (Conflict)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o nome de usuário ou e-mail já existem.
    """
    response = client.put(
        f'/accounts/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_account.username,
            'email': 'sama@sama.com',
            'password': 'sama',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Username or email already exists',
    }


def test_update_account_should_return_403_error_when_updating_another_account(
    client, other_account, token
):
    """
    Testa se o endpoint /accounts/{account_id} retorna erro 403 quando
    uma conta tenta atualizar os dados de outra conta.

    Verifica se a resposta da API contém o status code 403 (Forbidden)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    a conta não tem permissões suficientes.
    """
    response = client.put(
        f'/accounts/{other_account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'sama',
            'email': 'sama@sama.com',
            'password': 'sama',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_account_should_return_deletion_success_message(
    client, account, token
):
    """
    Testa se o endpoint /accounts/{account_id} retorna uma mensagem de sucesso
    quando uma conta é deletado.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém uma mensagem indicando que
    a conta foi deletado com sucesso.
    """
    response = client.delete(
        f'/accounts/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Account deleted successfully'}


def test_delete_account_should_return_403_error_when_deleting_another_account(
    client, other_account, token
):
    """
    Testa se o endpoint /accounts/{account_id} retorna erro 403 quando
    uma conta tenta deletar outra conta.

    Verifica se a resposta da API contém o status code 403 (Forbidden)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    a conta não tem permissões suficientes.
    """
    response = client.delete(
        f'/accounts/{other_account.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_account_should_return_account(client, account):
    """
    Testa se o endpoint /accounts/{account_id} retorna os dados de uma conta.
    Utiliza a fixture 'account' para criar uma conta no banco de dados.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados da conta criado.
    """
    response = client.get('/accounts/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': account.username,
        'email': account.email,
    }


def test_get_account_should_return_404_error_when_account_not_found(client):
    """
    Testa se o endpoint /accounts/{account_id} retorna erro 404 quando
    a conta não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    a conta não foi encontrado.
    """
    response = client.get('/accounts/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Account not found'}
