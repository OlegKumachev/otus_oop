import pytest

from api import (
    ArgumentsField,
    BirthDayField,
    CharField,
    ClientIDsField,
    DateField,
    EmailField,
    Field,
    GenderField,
    PhoneField,
)


@pytest.fixture
def char_field_class():
    field = CharField()
    field.name = "test"
    return field


@pytest.mark.parametrize("value", ["valid", "", None])
def test_char_field(char_field_class, value):
    char_field_class.validate(value)


@pytest.mark.parametrize("value", [1, 0.2, {}])
def test_char_field_not_valid(char_field_class, value):

    with pytest.raises(ValueError):
        char_field_class.validate(value)


@pytest.fixture
def agruments_class():
    field = ArgumentsField()
    field.name = "test"
    return field


@pytest.mark.parametrize("value", [{}, {"key": "value"}])
def test_arguments_valid(agruments_class, value):
    agruments_class.validate(value)


@pytest.mark.parametrize("value", ["srt", []])
def test_arguments_invalid(agruments_class, value):
    with pytest.raises(ValueError):
        agruments_class.validate(value)


@pytest.fixture
def email_class():
    field = EmailField()
    field.name = "test"
    return field


@pytest.mark.parametrize("value", ["name@email.ru", "2@mail.ru"])
def test_email_valid(email_class, value):
    email_class.validate(value)


@pytest.mark.parametrize("value", ["name$email.ru", "12323"])
def test_email_invalid(email_class, value):
    with pytest.raises(ValueError):
        email_class.validate(value)


@pytest.fixture
def phone_class():
    field = PhoneField()
    field.name = "test"
    return field


@pytest.mark.parametrize("value", [71234567890])
def test_phone_valid(phone_class, value):
    phone_class.validate(value)


@pytest.mark.parametrize("value", ["name$email.ru", 0.3123])
def test_phone_invalid(phone_class, value):
    with pytest.raises(ValueError):
        phone_class.validate(value)


@pytest.fixture
def date_class():
    field = DateField()
    field.name = "test"
    return field


@pytest.mark.parametrize("value", ["02.10.2002", "22.12.2002"])
def test_date_valid(date_class, value):
    date_class.validate(value)


@pytest.mark.parametrize("value", ["22.13.2002", "10.10.10", "1.10.10", "12,10,2000"])
def test_date_invalid(date_class, value):
    with pytest.raises(ValueError):
        date_class.validate(value)


@pytest.fixture
def birth_day_class():
    field = BirthDayField()
    field.name = "test"
    return field


@pytest.mark.parametrize("value", ["02.10.2002", "20.02.1991"])
def test_birth_day_valid(birth_day_class, value):
    birth_day_class.validate(value)


@pytest.mark.parametrize("value", ["22.12.1900", "19.02.1861"])
def test_birth_day_invalid(birth_day_class, value):
    with pytest.raises(ValueError):
        birth_day_class.validate(value)


@pytest.fixture
def gender_class():
    field = GenderField()
    field.name = "test"
    return field


@pytest.mark.parametrize("value", [1, 2, 0])
def test_gender_valid(gender_class, value):
    gender_class.validate(value)


@pytest.mark.parametrize("value", [3, "0", True, False])
def test_gender_invalid(gender_class, value):
    with pytest.raises(ValueError):
        gender_class.validate(value)


@pytest.fixture
def client_class():
    field = ClientIDsField()
    field.name = "test"
    return field


@pytest.mark.parametrize("value", [[1, 2, 3], [123, 2312, 4343]])
def test_client_valid(client_class, value):
    client_class.validate(value)


@pytest.mark.parametrize("value", [[], ["0"], "[]"])
def test_client_invalid(client_class, value):
    with pytest.raises(ValueError):
        client_class.validate(value)


def test_field_required():
    field = Field(required=True, nullable=True)
    field.name = "test"
    with pytest.raises(ValueError):
        field.validate(None)


def test_field_not_nullable():
    field = Field(required=False, nullable=False)
    field.name = "test"
    with pytest.raises(ValueError):
        field.validate(None)


def test_field_optional():
    field = Field(required=False, nullable=True)
    field.name = "test"
    field.validate(None)
    field.validate("")
