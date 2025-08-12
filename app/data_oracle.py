class DataOracle:

    def __init__(self) -> None:
        self.key_map = {}
        pass

    def get(self, key):
        if key in self.key_map:
            return self.key_map[key]
        return None

    def set(self, key, val):
        self.key_map[key] = val
        return "OK"

    def exists(self, key):
        return key in self.key_map