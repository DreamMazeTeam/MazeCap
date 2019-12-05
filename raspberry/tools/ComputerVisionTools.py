import tkinter as tk
import numpy as np
from threading import Thread


# Декоратор для запуска функции в отдельном потоке
# Возвращает указатель на поток
# Поток убьет себя в случае завершения главного потока
def thread(function: callable) -> callable:
    def wrapper(*args, **kwargs) -> Thread:
        _t = Thread(target=function, args=args, kwargs=kwargs)
        _t.daemon = True; _t.start(); return _t
    return wrapper


@thread
# функция запуска слайдера с настройкой цветов HSV
def createSliderHSV(colorMin: np.array, colorMax: np.array) -> None:
    windowRoot = tk.Tk()
    windowRoot.title("HSV Slider")

    labelMinH = tk.Label(windowRoot, text="Min H")
    labelMinH.grid(row=0, column=0)
    sliderMinH = tk.Scale(windowRoot, from_=180, to=0, orient=tk.VERTICAL, command=lambda x: colorMin.put(0, x))
    sliderMinH.config(width=30, length=500)
    sliderMinH.grid(row=1, column=0)
    sliderMinH.set(colorMin[0])

    labelMaxH = tk.Label(windowRoot, text="Max H")
    labelMaxH.grid(row=0, column=1)
    sliderMaxH = tk.Scale(windowRoot, from_=180, to=0, orient=tk.VERTICAL, command=lambda x: colorMax.put(0, x),)
    sliderMaxH.config(width=30, length=500)
    sliderMaxH.grid(row=1, column=1)
    sliderMaxH.set(colorMax[0])

    labelMinS = tk.Label(windowRoot, text="Min S")
    labelMinS.grid(row=0, column=2)
    sliderMinS = tk.Scale(windowRoot, from_=255, to=0, orient=tk.VERTICAL, command=lambda x: colorMin.put(1, x))
    sliderMinS.config(width=30, length=500)
    sliderMinS.grid(row=1, column=2)
    sliderMinS.set(colorMin[1])

    labelMaxS = tk.Label(windowRoot, text="Max S")
    labelMaxS.grid(row=0, column=3)
    sliderMaxS = tk.Scale(windowRoot, from_=255, to=0, orient=tk.VERTICAL, command=lambda x: colorMax.put(1, x))
    sliderMaxS.config(width=30, length=500)
    sliderMaxS.grid(row=1, column=3)
    sliderMaxS.set(colorMax[1])

    labelMinV = tk.Label(windowRoot, text="Min V")
    labelMinV.grid(row=0, column=4)
    sliderMinV = tk.Scale(windowRoot, from_=255, to=0, orient=tk.VERTICAL, command=lambda x: colorMin.put(2, x))
    sliderMinV.config(width=30, length=500)
    sliderMinV.grid(row=1, column=4)
    sliderMinV.set(colorMin[2])

    labelMaxV = tk.Label(windowRoot, text="Max V")
    labelMaxV.grid(row=0, column=5)
    sliderMaxV = tk.Scale(windowRoot, from_=255, to=0, orient=tk.VERTICAL, command=lambda x: colorMax.put(2, x))
    sliderMaxV.config(width=30, length=500)
    sliderMaxV.grid(row=1, column=5)
    sliderMaxV.set(colorMax[2])

    windowRoot.resizable(width=False, height=False)
    windowRoot.mainloop()


if __name__ == '__main__':
    c_min = np.array((0, 0, 0), np.uint8)
    c_max = np.array((0, 0, 0), np.uint8)
    createSliderHSV(c_min, c_max)
    while 1:
        pass
