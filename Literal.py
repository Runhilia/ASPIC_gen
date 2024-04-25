class Literal:
    def __init__(self, value, is_negative):
        self.value = value # string
        self.is_negative = is_negative # boolean

    def print(self):
        if self.is_negative:
            print("¬" + self.value, end="")
        else:
            print(self.value, end="")

    def __eq__(self, other):
        return self.value == other.value and self.is_negative == other.is_negative

    def get_value(self):
        return self.value

    def get_is_negative(self):
        return self.is_negative
