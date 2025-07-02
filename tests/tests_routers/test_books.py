from http import HTTPStatus

import factory
import factory.fuzzy

from madr.models.author import Author
from madr.models.book import Book


class AuthorFactory(factory.Factory):
    class Meta:
        model = Author

    name = factory.Faker('name')


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    title = factory.Faker('sentence', nb_words=3)
    year = factory.fuzzy.FuzzyInteger(1900, 2023)
    author_id = factory.SubFactory(AuthorFactory)


def test_create_book_withou_author(client, token):
    """
    Testa se o endpoint /books/ retorna erro 404 quando
    o autor não existe.
    """
    book_data = {
        'title': 'Dom Casmurro',
        'year': 1899,
        'author_id': 1,
    }
    response = client.post(
        '/books/',
        headers={'Authorization': f'Bearer {token}'},
        json=book_data,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not found'}


def test_create_book_should_return_created_book(client, token, session):
    """
    Testa se o endpoint /books/ cria um livro e retorna os
    dados do livro criado.

    Verifica se a resposta da API contém o status code 201 (Created) e
    se o corpo da resposta contém os dados do livro criado, incluindo
    o ID gerado automaticamente.
    """
    author = AuthorFactory(name='Machado de Assis')
    session.add(author)
    session.commit()
    book_data = {
        'title': 'Dom Casmurro',
        'year': 1899,
        'author_id': author.id,
    }
    response = client.post(
        '/books/',
        headers={'Authorization': f'Bearer {token}'},
        json=book_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'dom casmurro',
        'year': 1899,
        'author_id': author.id,
    }


def test_create_book_should_return_400_error_when_book_already_exists(
    client, token, session
):
    """
    Testa se o endpoint /books/ retorna erro 400 quando
    o livro já existe.

    Verifica se a resposta da API contém o status code 400 (Bad Request)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o título do livro já existe.
    """
    author = AuthorFactory(name='Machado de Assis')
    session.add(author)
    session.commit()
    book_data = {
        'title': 'Dom Casmurro',
        'year': 1899,
        'author_id': author.id,
    }
    client.post(
        '/books/',
        headers={'Authorization': f'Bearer {token}'},
        json=book_data,
    )
    response = client.post(
        '/books/',
        headers={'Authorization': f'Bearer {token}'},
        json=book_data,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Book already exists'}


def test_delete_book_should_return_404_error_when_book_does_not_exists(
    client, token
):
    """
    Testa se o endpoint /books/{book_id} retorna erro 404 quando
    o livro não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o livro não foi encontrado.
    """
    response = client.delete(
        '/books/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_delete_book_should_return_deleted_book(client, token, session):
    """
    Testa se o endpoint /books/{book_id} deleta um livro e retorna
    uma mensagem de sucesso.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém uma mensagem de sucesso indicando que
    o livro foi deletado.
    """
    author = AuthorFactory(name='Machado de Assis')
    session.add(author)
    session.commit()
    book = BookFactory(title='Dom Casmurro', year=1899, author_id=author.id)
    session.add(book)
    session.commit()

    response = client.delete(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book deleted successfully'}


def test_patch_book_should_return_404_error_when_book_does_not_exists(
    client, token
):
    """
    Testa se o endpoint /books/{book_id} retorna erro 404 quando
    o livro não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o livro não foi encontrado.
    """
    response = client.patch(
        '/books/1',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Novo Título'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_patch_book_should_return_updated_book(client, token, session):
    """
    Testa se o endpoint /books/{book_id} atualiza um livro e retorna
    os dados do livro atualizado.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do livro atualizado.
    """
    author = AuthorFactory(name='Machado de Assis')
    session.add(author)
    session.commit()
    book = BookFactory(title='Dom Casmurro', year=1899, author_id=author.id)
    session.add(book)
    session.commit()

    response = client.patch(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Dom Casmurro - Edição Especial'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': 'dom casmurro - edição especial',
        'year': 1899,
        'author_id': author.id,
    }


def test_patch_book_with_year_altered_should_return_updated_book(
    client, token, session
):
    """
    Testa se o endpoint /books/{book_id} atualiza o ano de um livro
    e retorna os dados do livro atualizado.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do livro atualizado com o
    novo ano.
    """
    author = AuthorFactory(name='Machado de Assis')
    session.add(author)
    session.commit()
    book = BookFactory(title='Dom Casmurro', year=1899, author_id=author.id)
    session.add(book)
    session.commit()
    response = client.patch(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'year': 1900},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': 'dom casmurro',
        'year': 1900,
        'author_id': author.id,
    }


def test_patch_book_should_return_400_error_when_title_already_exists(
    client, token, session
):
    """
    Testa se o endpoint /books/{book_id} retorna erro 400 quando
    o título do livro já existe.

    Verifica se a resposta da API contém o status code 400 (Bad Request)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o título do livro já existe.
    """
    author = AuthorFactory(name='Machado de Assis')
    session.add(author)
    session.commit()
    book1 = BookFactory(title='Dom Casmurro', year=1899, author_id=author.id)
    session.add(book1)
    session.commit()
    book2 = BookFactory(
        title='Memórias Póstumas de Brás Cubas',
        year=1881,
        author_id=author.id
    )
    session.add(book2)
    session.commit()
    response = client.patch(
        '/books/2',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Dom Casmurro'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Book already exists'}


def test_get_book_should_return_404_error_when_book_does_not_exists(
    client, token
):
    """
    Testa se o endpoint /books/{book_id} retorna erro 404 quando
    o livro não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o livro não foi encontrado.
    """
    response = client.get(
        '/books/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_get_book_should_return_book(client, token, session):
    """
    Testa se o endpoint /books/{book_id} retorna os dados do livro
    quando o livro existe.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do livro.
    """
    author = AuthorFactory(name='Machado de Assis')
    session.add(author)
    session.commit()
    book = BookFactory(title='Dom Casmurro', year=1899, author_id=author.id)
    session.add(book)
    session.commit()

    response = client.get(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': 'dom casmurro',
        'year': 1899,
        'author_id': author.id,
    }


def test_get_books_should_return_books(client, token, session):
    """
    Testa se o endpoint /books/ retorna uma lista de livros.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém uma lista de livros.
    """
    author = AuthorFactory(name='Machado de Assis')
    session.add(author)
    session.commit()
    book1 = BookFactory(title='Dom Casmurro', year=1899, author_id=author.id)
    book2 = BookFactory(
        title='Memórias Póstumas de Brás Cubas', year=1881, author_id=author.id
    )
    session.add(book1)
    session.add(book2)
    session.commit()
    expected_books = 2
    response = client.get(
        '/books/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books
    assert response.json() == {
        'books': [
            {'title': 'dom casmurro', 'year': 1899, 'author_id': 1, 'id': 1},
            {
                'title': 'memórias póstumas de brás cubas',
                'year': 1881,
                'author_id': 1,
                'id': 2
            }
        ]
    }
