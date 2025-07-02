from http import HTTPStatus

import factory
import factory.fuzzy

from madr.models.author import Author


class AuthorFactory(factory.Factory):
    class Meta:
        model = Author

    name = factory.Faker('name')


def test_create_author_should_return_created_author(client, token):
    """
    Testa se o endpoint /authors/ cria um autor e retorna os
    dados do autor criado.

    Verifica se a resposta da API contém o status code 201 (Created) e
    se o corpo da resposta contém os dados do autor criado, incluindo
    o ID gerado automaticamente.
    """
    author_data = {
        'name': 'machado de assis',
    }
    response = client.post(
        '/authors/',
        headers={'Authorization': f'Bearer {token}'},
        json=author_data,
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'Machado De Assis',
    }


def test_create_author_should_return_400_error_when_author_already_exists(
    client, token
):
    """
    Testa se o endpoint /authors/ retorna erro 409 quando
    o autor já existe.

    Verifica se a resposta da API contém o status code 409 (Conflict)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o nome do autor já existe.
    """
    client.post(
        '/authors/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'machado de assis',
        },
    )
    response = client.post(
        '/authors/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'machado de assis',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Author already exists'}


def test_delete_author_should_return_404_error_when_author_does_not_exists(
    client, token
):
    """
    Testa se o endpoint /authors/{author_id} retorna erro 404 quando
    o autor não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o autor não foi encontrado.
    """
    response = client.delete(
        '/authors/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not found'}


def test_delete_author_should_return_deleted_author(client, token, session):
    """
    Testa se o endpoint /authors/{author_id} deleta um autor existente.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém uma mensagem de sucesso indicando que
    o autor foi deletado.
    """
    author = AuthorFactory(name='Teste')
    session.add(author)
    session.commit()
    response = client.delete(
        f'/authors/{author.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Author deleted successfully'}


def test_patch_author_should_return_404_error_when_author_does_not_exists(
    client, token
):
    """
    Testa se o endpoint /authors/{author_id} retorna erro 404 quando
    o autor não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o autor não foi encontrado.
    """
    response = client.patch(
        '/authors/1',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Novo Nome'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not found'}


def test_patch_author_should_return_updated_author(client, token, session):
    """
    Testa se o endpoint /authors/{author_id} atualiza um autor existente.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do autor atualizado.
    """
    author = AuthorFactory(name='Machado d asis')
    session.add(author)
    session.commit()
    session.refresh(author)
    response = client.patch(
        f'/authors/{author.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Machado De Assis'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': author.id,
        'name': 'Machado De Assis',
    }


def test_patch_author_should_return_400_error_when_author_already_exists(
    client, token, session
):
    """
    Testa se o endpoint /authors/{author_id} retorna erro 400 quando
    o nome do autor já existe.

    Verifica se a resposta da API contém o status code 400 (Bad Request)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o autor já existe.
    """
    author1 = AuthorFactory(name='Machado De Assis')
    author2 = AuthorFactory(name='Manuel Bandeira')
    session.add(author1)
    session.add(author2)
    session.commit()

    response = client.patch(
        f'/authors/{author2.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Machado De Assis'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Author already exists'}


def test_get_author_should_return_404_error_when_author_does_not_exists(
    client, token
):
    """
    Testa se o endpoint /authors/{author_id} retorna erro 404 quando
    o autor não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o autor não foi encontrado.
    """
    response = client.get(
        '/authors/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not found'}


def test_get_author_should_return_author(client, token, session):
    """
    Testa se o endpoint /authors/{author_id} retorna os dados de um autor.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do autor solicitado.
    """
    author = AuthorFactory(name='Machado De Assis')
    session.add(author)
    session.commit()
    session.refresh(author)
    response = client.get(
        f'/authors/{author.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': author.id,
        'name': 'Machado De Assis',
    }


def test_get_authors_should_return_empty_list_when_no_authors_exist(
    client, token
):
    """
    Testa se o endpoint /authors/ retorna uma lista vazia quando
    não há autores.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta é uma lista vazia.
    """
    response = client.get(
        '/authors/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'authors': []}


def test_get_authors_should_return_list_of_authors(client, token, session):
    """
    Testa se o endpoint /authors/ retorna uma lista de autores.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém uma lista de autores.
    """
    author1 = AuthorFactory(name='Machado De assis')
    author2 = AuthorFactory(name='Manuel Bandeira')
    session.add(author1)
    session.add(author2)
    session.commit()

    response = client.get(
        '/authors/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'authors': [
            {'id': author1.id, 'name': 'Machado De Assis'},
            {'id': author2.id, 'name': 'Manuel Bandeira'},
        ]
    }


def test_get_authors_should_return_list_of_authors_with_name_filter(
    client, token, session
):
    """
    Testa se o endpoint /authors/ retorna uma lista de autores filtrados
    pelo nome.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém uma lista de autores filtrados pelo nome.
    """
    author1 = AuthorFactory(name='Machado De Assis')
    author2 = AuthorFactory(name='Clarice Lispector')
    author3 = AuthorFactory(name='Manuel bandeira')
    author4 = AuthorFactory(name='Carlos Drummond de Andrade')
    author5 = AuthorFactory(name='Paulo Leminski')
    author6 = AuthorFactory(name='Erico Verissimo')
    session.add(author1)
    session.add(author2)
    session.add(author3)
    session.add(author4)
    session.add(author5)
    session.add(author6)
    session.commit()

    response = client.get(
        '/authors/',
        headers={'Authorization': f'Bearer {token}'},
        params={'name': 'a'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'authors': [
            {'id': author1.id, 'name': 'Machado De Assis'},
            {'id': author2.id, 'name': 'Clarice Lispector'},
            {'id': author3.id, 'name': 'Manuel Bandeira'},
            {'id': author4.id, 'name': 'Carlos Drummond De Andrade'},
            {'id': author5.id, 'name': 'Paulo Leminski'},
        ]
    }
