import pytest

from madr.utils.sanitize_data import sanitize_text_in, sanitize_text_out


@pytest.mark.parametrize(
    ('input_str', 'expected'),
    [
        ('Machado de Assis', 'machado de assis'),
        ('Manuel        Bandeira', 'manuel bandeira'),
        ('Edgar Alan Poe         ', 'edgar alan poe'),
        (
            'Androides Sonham Com Ovelhas Elétricas?',
            'androides sonham com ovelhas elétricas',
        ),
        ('  breve  história  do tempo ', 'breve história do tempo'),
        (
            'O mundo assombrado pelos demônios',
            'o mundo assombrado pelos demônios',
        ),
    ],
)
def test_sanitize_input(input_str, expected):
    assert sanitize_text_in(input_str) == expected


@pytest.mark.parametrize(
    ('input_str', 'expected'),
    [
        ('machado de assis', 'Machado De Assis'),
        ('clarice lispector', 'Clarice Lispector'),
        ('manuel bandeira', 'Manuel Bandeira'),
        ('edgar alan poe', 'Edgar Alan Poe'),
        (
            'androides sonham com ovelhas elétricas',
            'Androides Sonham Com Ovelhas Elétricas',
        ),
    ],
)
def test_sanitize_output(input_str, expected):
    assert sanitize_text_out(input_str) == expected
