from api import ClientsInterestsRequest, OnlineScoreRequest


def test_online_score_request_phone_email():
    f = OnlineScoreRequest(phone="79175002040", email="name@mail.ru")
    assert f.validate() is True
    assert len(f.errors) == 0


def test_online_score_has_all():
    f = OnlineScoreRequest(
        phone="79175002040",
        email="a@b.ru",
        first_name="a",
        last_name="b",
    )
    assert f.validate() is True
    assert sorted(f.context["has"]) == ["email", "first_name", "last_name", "phone"]


def test_online_score_request_first_name_last_name():
    f = OnlineScoreRequest(first_name="first_name", last_name="last_name")
    assert f.validate() is True
    assert len(f.errors) == 0


def test_online_score_request_gender_birthday():
    f = OnlineScoreRequest(gender=2, birthday="20.02.1991")

    assert f.errors == {}


def test_online_score_request_gender_birthday_erroe():
    f = OnlineScoreRequest(
        gender=1,
    )
    f.validate()
    assert f.context["has"] == ["gender"]
    assert f.errors["arguments"] == "Должна быть заполнена хотя бы одна пара полей"


def test_client_interest():
    c = ClientsInterestsRequest(client_ids=[1, 2], date="03.09.1993")
    c.validate()
    assert c.context["nclients"] == 2
