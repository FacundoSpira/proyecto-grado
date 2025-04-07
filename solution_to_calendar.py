from generate_schedule import generate_schedule_csv


class Variable:
    def __init__(self, name, value):
        self.name = name
        self._value = float(value)

    def value(self):
        return self._value


with open("solutions/1s2p/solution_79.sol", "r") as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines if line.startswith("x")]

    variables = [
        Variable(name, value) for name, value in [line.split(" ") for line in lines]
    ]

generate_schedule_csv(variables, "schedule_test.csv")
