"""
    О модулях:
    Каждый модуль должен иметь:
        1) Главный генератор ( def main() )
        2) Переменую в которой хранятся результаты вычислений ( DATA )
        3) Переменая с названием модуля ( TAG )


    Алгоритм:
    Генераторы гланых генераторов хранятся в переменой MODULES
    Каждый главный генератор имеет структуру:
        1) Запуск (Инициализация) - возвращает 1
        2) Оснвной цикл - возвращает результаты вычислений (tuple) с видом: (module.Tag, module.Data)
        3) Конец (Выход) - возвращает 0

        Шаблон:

        def main(*args, **kwargs):
            # Init generator
            yield 1  # send init code

            # Main loop
            while <condition>:
                data = yield None  # Getting data from other modules
                # some actions
                yield TAG, DATA  # Returning module tag and data in the end of loop

            # Returning an exit code of generator
            yield 0


"""

import raspberry.modules.ComputerVision as cv  # Потключение модуля
cv.argv = cv.parser.parse_args("-d --show local".split())  # Аргументы запуска модуля


MODULES_DATA = {}  # Тут хранятся результаты вычислений всех модулей
MODULES = [  # Тут хранятся главные генераторы всех модулей
    cv.main()
]


# Запускает генераторы
def initModules(*args, **kwargs) -> None:
    for module in MODULES:
        module.send(None)


# Главный цикл програмы
def loopModules(*args, **kwargs) -> None:
    while len(MODULES) > 0:
        for module in MODULES:
            ret = module.send(MODULES_DATA)

            if ret == 0:
                MODULES.remove(module)

            else:
                data = module.send(None)
                if data == 0:
                    MODULES.remove(module)

                else:
                    MODULES_DATA.update({data[0]: data[1]})


if __name__ == '__main__':
    initModules()
    loopModules()



