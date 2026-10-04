import pytest

from api import BaseRequest, CharField


def test_field_collected():
    class Foo(BaseRequest):
        name = CharField()

    assert "name" in Foo._fields


def test_fields_inherited():
    class Parent(BaseRequest):
        a = CharField()

    class Child(Parent):
        b = CharField()

    assert "a" in Child._fields
    assert "b" in Child._fields


def test_non_field_not_collected():
    class Foo(BaseRequest):
        name = CharField()
        other = 42

    assert "other" not in Foo._fields


def test_base_inti():
    class Foo(BaseRequest):
        name = CharField()

    f = Foo()
    assert f.name is None


def test_base_init_sets_value():
    class Foo(BaseRequest):
        name = CharField()

    f = Foo(name="abc")
    assert f.name == "abc"


def test_base_errors_and_contex():
    class Foo(BaseRequest):
        name = CharField()

    f = Foo()
    assert f.errors == {}
    assert f.context == {}


def test_base_validate():
    class Foo(BaseRequest):
        name = CharField(required=True)

    f = Foo(name="a")
    assert f.validate() is True
    assert f.errors == {}


def test_base_invalid():
    class Foo(BaseRequest):
        name = CharField(required=True)

    f = Foo(name=1)
    assert f.validate() is False
    assert f.errors["name"] == "Поле 'name' должно быть строкой"


def test_base_validate_invalid():
    class Foo(BaseRequest):
        name = CharField(required=True)
        name1 = CharField(required=True)
        name2 = CharField(required=True)

    f = Foo(name=1)
    assert f.validate() is False
    assert set(f.errors.keys()) == {"name", "name1", "name2"}


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, True),
        (False, True),
        ("abc", True),
        (123, True),
        ("", False),
        (None, False),
    ],
)
def test_is_filled(value, expected):
    assert BaseRequest.is_filled(value) == expected
