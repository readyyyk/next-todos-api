def without_keys(d: dict, keys: list[str]) -> dict:
    return {x: d[x] for x in d if x not in keys}


class JWTPayloadError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
