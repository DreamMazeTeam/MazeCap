import raspberry.__main__ as environment

environment.MODULES = []
environment.MODULES_DATA = {}


def main(*args, **kwargs) -> None:
    # Инициализация модуля
    yield 1  # Код удачной инициализации

    #   <условие>
    while True:
        data = yield None  # Получение глобальных вычислений

        if data == "exit":
            break

        result = 0
        yield result  # Вывод рузультатов

    yield 0  # Выход из модуля


if __name__ == '__main__':
    environment.initModules()
    environment.loopModules()
