import schedule
import time


def test(param_1:str, param_2:str)->None:
    print(f"param_1:{param_1}\tparam_2:{param_2}")

param_1: str = "param_1"
param_2: str = "param_2"
schedule.every(1).seconds.until("19:45").do(test, param_1='hola1', param_2='hola2')
while True:
    schedule.run_pending()
    time.sleep(1)


