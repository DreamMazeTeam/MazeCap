import os
import json

"""

Кастомный модульный импортер,
Для того что бы запустить новый модуль,
Достаточно будет поместить его в папку modules

"""

MODULES = []
MODULES_PATH = "raspberry.modules"

mod = None
for module in os.listdir("modules\\"):
    if "py" in module.split('.'):
        exec(f"import {MODULES_PATH}.{'.'.join(module.split('.')[:-1])} as mod")
        MODULES += [mod]


if __name__ == '__main__':
    pass



