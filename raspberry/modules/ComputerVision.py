import cv2
import msvcrt
import argparse
import numpy as np

# Аргументы запуска скрипта
# --display [remote, local]
# Выводить ли изображение, если да то куда
# remote - удаленно
# local - локально
parser = argparse.ArgumentParser()
parser.add_argument('-d', "--debug", action="store_true", default=False)
parser.add_argument('-s', "--show", type=str, choices=["remote", "local"], action="store", default=False)
argv = parser.parse_args()


# Константы
if __name__ == "__main__":
    TM_PATH = "..\\templates\\"
else:
    TM_PATH = "templates\\"

CONST_TEMPLATE_SIZE = (10, 15)
TEMPLATE_MATCH_VALUE = 0.85
TEMPLATES = {
    "H": cv2.resize(cv2.imread(f"{TM_PATH}H.png"), CONST_TEMPLATE_SIZE),
    "S": cv2.resize(cv2.imread(f"{TM_PATH}S.png"), CONST_TEMPLATE_SIZE),
    "U": cv2.resize(cv2.imread(f"{TM_PATH}U.png"), CONST_TEMPLATE_SIZE),
}
COLOR_AREA = 100.0
DEBUG_COLOR = (255, 0, 0)
COLORS = {
    "green": [np.array((55, 250, 250), np.uint8), np.array((65, 255, 255), np.uint8)],
    "yellow": [np.array((25, 250, 250), np.uint8), np.array((35, 255, 255), np.uint8)],
    "red": [np.array((0, 250, 250), np.uint8), np.array((10, 255, 255), np.uint8)]
}
CC_DATA = {}


# Фунция для работы с окнами в cv2.namedWindow
# Исключительно для отладки
def mouseCallback(event, x, y, flag, param) -> None:
    # Ставит камеру на паузу
    if event == cv2.EVENT_LBUTTONDBLCLK:
        CC_DATA[param][0] = not CC_DATA[param][0]


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


# Генератор захвата камеры
# Принимает обьект cv2.VideoCapture и тэг функции
# Тэг нужен что бы понять какая камера видит цвет или букву
# Генерирует словарь (dict) вида:
# {тэг: [статус, буква, цвет] }, пример: {"camera_left: [True, "H", "red"]}
# статус показывает работает ли камера или нет
def captureCamera(camera: cv2.VideoCapture, tag: str = None):
    CC_DATA[tag] = [True, "", ""]
    yield None

    while camera.isOpened():
        flag, frame = camera.read()

        if flag and CC_DATA[tag][0]:

            CC_DATA[tag] = [
                True,
                getLetterFromFrame(frame),
                getColorFromFrame(frame)
            ]

            if argv.show:
                cv2.imshow(tag, frame)

        yield None


# todo
# Главная функция
# аргуметы аргс и кв для красоты)
# возвращает целое число, поже для обработки ошибок
# когда поставим код на робота нужно будет переписать
def main(*args, **kwargs):
    cap = cv2.VideoCapture(0)

    # это очередь из камер
    queue = [
        captureCamera(cap, "Camera-first"),
        captureCamera(cap, "Camera-secod"),
        captureCamera(cap, "Camera-third"),
        captureCamera(cap, "Camera-forth")
    ]

    # Запускаем камеры
    for camera in queue:
        camera.send(None)

    # Привязываем фунцию обработки мыши
    if argv.show:
        for tag in CC_DATA:
            cv2.namedWindow(tag)
            cv2.setMouseCallback(tag, mouseCallback, param=tag)

    # Start up
    yield 1

    while True:
        for camera in queue:
            camera.send(None)

        if argv.show:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                break

        else:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'1':
                    break

        yield None

    cap.release()
    yield 0


if __name__ == "__main__":
    mod = main()
    while mod.send(None) != 0:
        pass
