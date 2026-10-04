from unittest.mock import patch

from api import MethodRequest, method_handler


def test_method_request_is_admin():
    r = MethodRequest(login="admin", token="x", arguments={}, method="x")
    assert r.is_admin is True


def test_method_request_is_not_admin():
    r = MethodRequest(login="user", token="x", arguments={}, method="x")
    assert r.is_admin is False


def test_method_request_validate_missing():
    r = MethodRequest()
    assert r.validate() is False
    assert "login" in r.errors
    assert "method" in r.errors
    assert "arguments" in r.errors


def test_method_request_validate_ok():
    r = MethodRequest(login="user", token="x", arguments={}, method="online_score")
    assert r.validate() is True


def test_empty_request():
    request = {"body": {}}
    ctx = {}
    response, code = method_handler(request, ctx, None)
    assert code == 422
    assert response


@patch("api.check_auth", return_value=False)
def test_bad_auth(mock_auth):
    request = {
        "body": {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "token": "bad",
            "arguments": {},
        }
    }
    response, code = method_handler(request, {}, None)
    assert code == 403
    assert response == {"error": "Forbidden"}
    mock_auth.assert_called_once()


@patch("api.check_auth", return_value=True)
@patch("api.scoring.get_score", return_value=5.0)
def test_online_score_ok(mock_get_score, mock_auth):
    request = {
        "body": {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "token": "x",
            "arguments": {"phone": "79175002040", "email": "a@b.ru"},
        }
    }
    ctx = {}
    response, code = method_handler(request, ctx, None)
    assert code == 200
    assert response == {"score": 5.0}
    mock_get_score.assert_called_once()


@patch("api.check_auth", return_value=True)
@patch("api.scoring.get_score", return_value=5.0)
def test_online_score_admin(mock_get_score, mock_auth):
    request = {
        "body": {
            "login": "admin",
            "method": "online_score",
            "token": "x",
            "arguments": {"phone": "79175002040", "email": "a@b.ru"},
        }
    }
    response, code = method_handler(request, {}, None)
    assert code == 200
    assert response == {"score": 42}
    mock_get_score.assert_not_called()


@patch("api.check_auth", return_value=True)
@patch("api.scoring.get_interests", return_value=["books", "hi-tech"])
def test_clients_interests_ok(mock_get_interests, mock_auth):
    request = {
        "body": {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "clients_interests",
            "token": "x",
            "arguments": {"client_ids": [1, 2]},
        }
    }
    ctx = {}
    response, code = method_handler(request, ctx, None)
    assert code == 200
    assert response == {"1": ["books", "hi-tech"], "2": ["books", "hi-tech"]}
    assert ctx["nclients"] == 2
    assert mock_get_interests.call_count == 2
