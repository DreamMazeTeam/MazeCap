import raspberry.modules.ComputerVision as cv
cv.argv = cv.parser.parse_args("-d --show local")


MODULE_EXIT_CODE = 0
MODULES_INPUT = []
MODULES_OUTPUT = []
MODULES = [
    cv.main()
]


def initModules(*args, **kwargs) -> None:
    for module in MODULES:
        module.send(None)


def loopModules(*args, **kwargs) -> None:
    while len(MODULES) > 0:
        for module in MODULES:
            if module.send(MODULES_INPUT) == 0:
                MODULES.remove(module)


if __name__ == '__main__':
    initModules()
    loopModules()



