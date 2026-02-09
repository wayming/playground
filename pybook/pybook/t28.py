import collections


class CommandQueue:
    def __init__(self):
        self._commands = collections.deque()

    def execute(self, command: str):
        tokens = command.split()
        if tokens[0] == "PUSH":
            if len(tokens) != 2 or not tokens[1].isdecimal():
                raise ValueError("Invalid Command")
            self._commands.append(int(tokens[1]))
        if tokens[0] == "POP":
            if len(tokens) != 1:
                raise ValueError("Invalid Command")
            return self._commands.popleft()
        if tokens[0] == "SHOW":
            if len(tokens) != 1:
                raise ValueError("Invalid Command")
            return [n for n in self._commands]
