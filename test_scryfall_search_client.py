from api.scryfall_search import (
    ScryfallSearchClient,
)


class FakeResponse:
    def __init__(
        self,
        status_code,
        payload,
        headers=None,
    ):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(
        self,
        url,
        params=None,
        headers=None,
        timeout=None,
    ):
        self.calls.append(
            {
                "url": url,
                "params": params,
                "headers": headers,
                "timeout": timeout,
            }
        )

        if url.endswith("/sets"):
            return FakeResponse(
                200,
                {
                    "object": "list",
                    "data": [
                        {
                            "code": "tla",
                            "name": ("Avatar: " "The Last Airbender"),
                        }
                    ],
                },
            )

        if url.endswith("/cards/autocomplete"):
            return FakeResponse(
                200,
                {
                    "object": "catalog",
                    "data": [
                        "Aang, Swift Savior",
                    ],
                },
            )

        if url.endswith("/cards/random"):
            return FakeResponse(
                200,
                {
                    "object": "card",
                    "name": "Aang, Swift Savior",
                },
            )

        return FakeResponse(
            200,
            {
                "object": "list",
                "total_cards": 1,
                "has_more": False,
                "data": [
                    {
                        "object": "card",
                        "name": "Aang, Swift Savior",
                    }
                ],
            },
        )


print("=" * 60)
print("SCRYFALL SEARCH CLIENT TEST")
print("=" * 60)


session = FakeSession()

client = ScryfallSearchClient(
    session=session,
    min_request_interval=0,
)


result = client.search_cards(
    query="name:Aang legal:pioneer",
    page=2,
    unique="cards",
    order="name",
    direction="asc",
    include_extras=True,
)

if result["total_cards"] != 1:
    raise RuntimeError("Ожидалась одна найденная карта")


search_call = session.calls[-1]

if search_call["url"] != "https://api.scryfall.com/cards/search":
    raise RuntimeError("Использован неверный URL поиска")

if search_call["params"]["page"] != 2:
    raise RuntimeError("Номер страницы не передан")

if search_call["params"]["include_extras"] != "true":
    raise RuntimeError("Параметр include_extras не передан")


suggestions = client.autocomplete("Aang")

if suggestions != [
    "Aang, Swift Savior",
]:
    raise RuntimeError("Автодополнение вернуло неверные данные")


sets = client.get_all_sets()

if sets[0]["code"] != "tla":
    raise RuntimeError("Список наборов загружен неверно")


random_card = client.get_random_card()

if random_card["name"] != "Aang, Swift Savior":
    raise RuntimeError("Случайная карта загружена неверно")


print("Search calls:", len(session.calls))
print("Found:", result["data"][0]["name"])
print("Autocomplete:", suggestions[0])
print("Set:", sets[0]["name"])
print("Random:", random_card["name"])

print()
print("RESULT: OK")
