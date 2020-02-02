import cv2
import argparse
import numpy as np



#  Глобальные переменые модуля
TAG = "ComputerVision"
CAMERA_SETTINGS = {}
DATA = {}

#  Настройки модуля
TM_PATH = "images/templates/"

#  Настройки изображения
CONST_TEMPLATE_SIZE = (10, 15)
TEMPLATE_MATCH_VALUE = 0.5
TEMPLATES = {
    "H": cv2.resize(cv2.imread(f"{TM_PATH}H.png"), CONST_TEMPLATE_SIZE),
    "S": cv2.resize(cv2.imread(f"{TM_PATH}S.png"), CONST_TEMPLATE_SIZE),
    "U": cv2.resize(cv2.imread(f"{TM_PATH}U.png"), CONST_TEMPLATE_SIZE),
}

#  Настройки камер
COLOR_AREA = 100.0
DEBUG_COLOR = (255, 0, 0)
CAMERA_SIZE = (160*4, 120*4)
COLORS = {
    "green": [np.array((55, 250, 0), np.uint8), np.array((65, 255, 255), np.uint8)],
    "yellow": [np.array((25, 250, 0), np.uint8), np.array((35, 255, 255), np.uint8)],
    "red": [np.array((0, 250, 0), np.uint8), np.array((10, 255, 255), np.uint8)]
}


parser = argparse.ArgumentParser()
parser.add_argument('-d', "--debug", action="store_true", default=False)
parser.add_argument('-s', "--show", type=str, choices=["remote", "local"], action="store", default=False)
argv = parser.parse_args()

"""
    Управление мышью в режиме отладки:
        1) контрл + двойной щелчок левой кнопки мыши --> смена с цветов с BGR на HSV, и наоборот
        2) двойной щелчок левой кнопки мыши --> заморозка камеры
        3) шифт + двойной щелчок левой кнопки мыши --> показывает цвет пикселя            
"""


# Фунция для работы с окнами в cv2.namedWindow
# Исключительно для отладки
def mouseCallback(event, x, y, flag, param) -> None:
    if flag == 9 and event == cv2.EVENT_LBUTTONDBLCLK:  # контрл + двойной щелчок левой кнопки мыши
        CAMERA_SETTINGS[param]["HSV"] = not CAMERA_SETTINGS[param]["HSV"]
    elif flag == 17 and event == cv2.EVENT_LBUTTONDBLCLK:  # шифт + двойной щелчок левой кнопки мыши
        CAMERA_SETTINGS[param]["PX_COLOR"] = DATA[param][3][y, x]
    elif flag == 33 and event == cv2.EVENT_LBUTTONDBLCLK:  # контрл + двойной щелчок левой кнопки мыши
        print("alt")  # Пока ничего=)
    elif flag == 1 and event == cv2.EVENT_LBUTTONDBLCLK:  # Дабл клик
        DATA[param][0] = not DATA[param][0]  # Ставит камеру на паузу


# Окно информации о состоянии камер
def infoWindow(*args, **kwargs):
    image = np.zeros((512, 512, 3), np.uint8)
    default = cv2.FONT_ITALIC, 0.5, (255, 0, 0), 1
    x, y = 10, 30

    cv2.putText(image, "Camera settings", (x, y), *default)
    for camera in CAMERA_SETTINGS:
        cv2.putText(image, f"{camera}:", (x + 20, y + 30), *default)
        y += 30

        for setting in CAMERA_SETTINGS[camera]:
            cv2.putText(image, f"{setting}: {CAMERA_SETTINGS[camera][setting]}", (x + 40, y + 30), *default)
            y += 30


    cv2.putText(image, "Camera data", (x, y+30), *default)
    y += 30

    for camera in DATA:
        cv2.putText(image, f"{camera} -> {DATA[camera][:-1]}", (x+20, y+30), *default)
        y += 30

    cv2.imshow("INFO", image)


# Функция поиска контуров в кадре
# Принимает кадр, аргументы трешолда: thresh, maxval
# Возвращает результат выполнения функции cv2.findContours():
def findContours(frame: np.ndarray, _thresh: tuple) -> tuple:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, _thresh[0], _thresh[1], cv2.THRESH_BINARY_INV)
    return cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


# Функция поиска самого большого обьекта
# Принимает в себя список полученый из cv2.findContours()
# Возвращает кортеж вида: (x, y, w, h)
# x - координа оX левого верхнего угла
# y - коордтната oY левого верхнего угла
# w - ширина квадрата
# h - высота квадрата
def findBiggestRect(contours_array: list) -> tuple:
    if len(contours_array) > 0:
        sqr, idx = 0, 0
        for index, contour in enumerate(contours_array):
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > sqr:
                sqr = w * h
                idx = index
        return cv2.boundingRect(contours_array[idx])
    else:
        return tuple()


# Функция проверяет есть ли буква в кадре
# Принимает один аргумент: кадр
# Возвращает одну из букв заданых в словаре TEMPLATES
# В случае не удачи возвращает пустую строку
def getLetterFromFrame(frame: np.ndarray) -> str:
    contours, hierarchy = findContours(frame, (55, 255))
    shape = findBiggestRect(contours)

    if len(shape) == 4:
        x, y, w, h = shape
        rect = frame[y:y+h, x:x+w]
        rect = cv2.resize(rect, CONST_TEMPLATE_SIZE)

        for letter in TEMPLATES:
            match = cv2.matchTemplate(rect, TEMPLATES[letter], cv2.TM_CCOEFF_NORMED)
            if match[0][0] >= TEMPLATE_MATCH_VALUE:
                if argv.debug:
                    cv2.rectangle(frame, (x-3, y-3), (x+w+3, y+h+3), DEBUG_COLOR, 2)
                return letter

    return ""


# Функция проверяет есть ли цвет в кадре
# Принимает один аргумент: кадр
# Возвращает одну из букв заданых в словаре TEMPLATES
# В случае не удачи возвращает пустую строку
def getColorFromFrame(frame: np.ndarray) -> str:
    hsvimg = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for color in COLORS:
        mask = cv2.inRange(hsvimg, COLORS[color][0], COLORS[color][1])
        moments = cv2.moments(mask, 1)

        if moments['m00'] > COLOR_AREA:

            if argv.debug:
                x = int(moments['m10'] / moments['m00'])
                y = int(moments['m01'] / moments['m00'])
                cv2.circle(frame, (x, y), 10, DEBUG_COLOR, -1)

            return color

    return ""


# Ввод с клавиатуры
# Метод чтения зависит от флага запуска
# Если есть флаг --show то чтение будет происходить через cv2
# Иначе с помощью модуля msvcrt
def keyboardInput(*args, **kwargs) -> int:
    if argv.show:

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            cv2.destroyAllWindows()
            return -1
    return 0


# Генератор захвата камеры
# Принимает обьект cv2.VideoCapture и тэг функции
# Тэг нужен что бы понять какая камера видит цвет или букву
# Генерирует словарь (dict) вида:
# {тэг: [статус, буква, цвет, (указатель)кадр] }, пример: {"camera_left: [True, "H", "red", np.ndarray()]}
# статус показывает работает ли камера или нет
def captureCamera(camera: cv2.VideoCapture, tag: str = None, resolution: list = None):
    resolution = [512, 512] if resolution is None else resolution  # Параметр по умолчанию
    frame = np.zeros((512, 512, 3), np.uint8)  # Пустой кадр
    DATA[tag] = [True, "", "", frame]  # Начальные результаты камеры
    CAMERA_SETTINGS[tag] = {"HSV": False}  # Дефолтные настройки камеры
    yield None  # Конец инициализации генератора самеры

    if argv.debug and argv.show:  #
        cv2.namedWindow(tag)
        cv2.setMouseCallback(tag, mouseCallback, param=tag)

    while camera.isOpened():
        if DATA[tag][0]:
            flag, frame = camera.read()

            if flag:
                DATA[tag] = [
                    True,
                    getLetterFromFrame(frame),
                    getColorFromFrame(frame),
                    frame
                ]

        if argv.show:
            frame = cv2.resize(frame, CAMERA_SIZE)
            cv2.resizeWindow(tag, *CAMERA_SIZE)
            if argv.debug and CAMERA_SETTINGS[tag]["HSV"]:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                DATA[tag][3] = frame
            cv2.imshow(tag, frame)

        yield None


# Главный генератор
# аргуметы аргс и кв для красоты)
# возвращает целое число, поже для обработки ошибок
# когда поставим код на робота нужно будет переписать
def main(*args, **kwargs):
    cap = cv2.VideoCapture(0)  # Это камера
    cap.set(3, 128)  # Высота 128 писелей
    cap.set(4, 128)  # Ширина 128 пикселей


    queue = [  # это очередь из камер
        captureCamera(cap, "Camera1"),
        captureCamera(cap, "Camera2")
    ]

    for camera in queue:
        camera.send(None)  # Запускаем камеры

    yield 1  # Start up

    while True:
        data = yield None

        for camera in queue:
            camera.send(None)

        if argv.debug:
            infoWindow()

        if keyboardInput() == -1:
            break

        yield TAG, DATA

    cap.release()
    yield 0


if __name__ == "__main__":
    mod = main()
    argv = parser.parse_args(("-d --show local".split()))
    while mod.send(None) != 0:
        pass