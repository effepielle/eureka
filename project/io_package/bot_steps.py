from typing import Callable

class BotSteps:
    def __init__(self) -> None:
        self._steps = []
        self._current_step = 0

    def register_step(self, func: Callable) -> None:
        assert func is not None
        self._steps.append(func)

    def next(self) -> Callable:
        self._current_step += 1
        if self._current_step >= len(self._steps):
            return None
        else:
            return self._steps[self._current_step - 1]