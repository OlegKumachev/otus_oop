import datetime
import hashlib
import json
import logging
import uuid
from argparse import ArgumentParser
from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer,
)
from typing import Callable
import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500

ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}


class Field:
    def __init__(self, required=False, nullable=True):

        self.required = required
        self.nullable = nullable

    def validate(self, value):

        if value is None or value == "":
            if self.required:
                raise ValueError(f"Поле '{self.name}' обязательно")
            if not self.nullable:
                raise ValueError(f"Поле '{self.name}' не может быть пустым")
            return
        self.validate_value(value)

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):

        instance.__dict__[self.name] = value

    def validate_value(self, value):
        pass


class CharField(Field):
    def validate_value(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Поле '{self.name}' должно быть строкой")


class ArgumentsField(Field):
    def validate_value(self, value):
        if not isinstance(value, dict):
            raise ValueError(f"Поле '{self.name}' должно быть словарём")


class EmailField(CharField):

    def validate_value(self, value):

        super().validate_value(value)

        if "@" not in value:
            raise ValueError(f"Поле '{self.name}' должно содержать @")


class PhoneField(Field):
    def validate_value(self, value):
        s = str(value)
        if len(s) != 11 or s[0] != "7" or not s.isdigit():
            raise ValueError(
                f"Поле '{self.name}' должно быть номером из 11 цифр, начинающимся с 7"
            )


class DateField(Field):
    def validate_value(self, value):
        date_format = "%d.%m.%Y"
        try:
            datetime.datetime.strptime(value, date_format)
        except ValueError:
            raise ValueError(
                f"Поле '{self.name}' должно быть датой в формате DD.MM.YYYY"
            )


class BirthDayField(DateField):
    def validate_value(self, value):
        super().validate_value(value)
        birth = datetime.datetime.strptime(value, "%d.%m.%Y").date()
        today = datetime.datetime.today().date()
        age = (
            today.year
            - birth.year
            - ((today.month, today.day) < (birth.month, birth.day))
        )
        if age > 70:
            raise ValueError(f"Поле '{self.name}' должно быть не старше 70 лет")


class GenderField(Field):
    def validate_value(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"Поле '{self.name}' должно быть числом")
        if value not in [0, 1, 2]:
            raise ValueError(f"Поле '{self.name}' должно быть 0, 1 или 2")


class ClientIDsField(Field):
    def validate_value(self, value):
        if not isinstance(value, list):
            raise ValueError(f"Поле '{self.name}' должно быть списком")
        if not value:
            raise ValueError(f"Поле '{self.name}' не может быть пустым")
        for item in value:
            if not isinstance(item, int) or isinstance(item, bool):
                raise ValueError(f"Поле '{self.name}' должно содержать числа")


class FieldsMeta(type):

    def __new__(fmc, name, base, namespace):
        cls = super().__new__(fmc, name, base, namespace)
        fields = {}
        for b in base:
            fields.update(getattr(b, "_fields", {}))
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value
        cls._fields = fields

        return cls


class BaseRequest(metaclass=FieldsMeta):
    def __init__(self, **kwargs):
        self.errors = {}
        self.context = {}

        for name, _ in self._fields.items():
            value = kwargs.get(name)
            setattr(self, name, value)

    @staticmethod
    def is_filled(value):
        return value is not None and value != ""

    def validate(self):

        self.errors = {}
        for name, field in self._fields.items():
            value = getattr(self, name)
            try:
                field.validate(value)
            except ValueError as e:
                self.errors[name] = str(e)
        return not self.errors


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def validate(self):
        super().validate()
        if self.client_ids:
            self.context["nclients"] = len(self.client_ids)
        return not self.errors


class OnlineScoreRequest(BaseRequest):

    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self):
        super().validate()

        pairs = [
            ("phone", "email"),
            ("first_name", "last_name"),
            ("gender", "birthday"),
        ]
        if not any(
            self.is_filled(getattr(self, a)) and self.is_filled(getattr(self, b))
            for a, b in pairs
        ):
            self.errors["arguments"] = "Должна быть заполнена хотя бы одна пара полей"

        self.context["has"] = [
            name for name in self._fields if self.is_filled(getattr(self, name))
        ]

        return not self.errors


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=False, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self) -> bool:
        return self.login == ADMIN_LOGIN


def check_auth(request: MethodRequest) -> bool:
    if request.is_admin:
        digest = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf-8")
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            (request.account + request.login + SALT).encode("utf-8")
        ).hexdigest()
    return digest == request.token


def method_handler(request, ctx, settings):
    body = request["body"]
    method_request = MethodRequest(**body)
    if not method_request.validate():
        return method_request.errors, INVALID_REQUEST

    if not check_auth(method_request):
        return {"error": "Forbidden"}, FORBIDDEN
    method_name = method_request.method
    arguments = method_request.arguments

    if method_name == "online_score":
        score_request = OnlineScoreRequest(**arguments)
        if not score_request.validate():
            return score_request.errors, INVALID_REQUEST
        ctx.update(score_request.context)  # has
        if method_request.is_admin:
            return {"score": 42}, OK
        score = scoring.get_score(
            phone=score_request.phone,
            email=score_request.email,
            birthday=score_request.birthday,
            gender=score_request.gender,
            first_name=score_request.first_name,
            last_name=score_request.last_name,
        )
        return {"score": score}, OK

    if method_name == "clients_interests":
        interests_request = ClientsInterestsRequest(**arguments)
        if not interests_request.validate():
            return interests_request.errors, INVALID_REQUEST
        ctx.update(interests_request.context)
        response = {}
        for client_id in interests_request.client_ids:
            response[str(client_id)] = scoring.get_interests(cid=str(client_id))
        return response, OK

    return {"error": "Unknown method"}, INVALID_REQUEST


class MainHTTPHandler(BaseHTTPRequestHandler):
    router: dict[str, Callable] = {"method": method_handler}

    def get_request_id(self, headers) -> str:
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self) -> None:
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, {}
                    )
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode("utf-8"))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", action="store", type=int, default=8080)
    parser.add_argument("-l", "--log", action="store", default=None)
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )

    server = HTTPServer(("localhost", args.port), MainHTTPHandler)

    logging.info("Starting server at %s" % args.port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
