from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """
    Gera um hash da senha fornecida.
    Esta função utiliza o PasswordHash recomendado para criar um hash seguro
    da senha, com a biblioteca pwdlib. Esta função é útil para armazenar senhas
    de forma segura no banco de dados.

    Args:
        password (str): A senha a ser hasheada.

    Returns:
        str: O hash da senha.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.
    Esta função utiliza o PasswordHash recomendado para verificar se a senha
    fornecida corresponde ao hash armazenado. É útil para autenticação de
    usuários, garantindo que a senha fornecida pelo usuário seja válida.

    Args:
        plain_password (str): A senha fornecida pelo usuário.
        hashed_password (str): O hash da senha armazenado.

    Returns:
        bool: True se a senha corresponder ao hash, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)
