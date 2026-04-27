import threading
import time

event = threading.Event()


def waiter():
    print("Ожидаю сигнала...")
    event.wait()
    print("Сигнал получен, продолжаю работу")


def signaler():
    time.sleep(2)
    print("Отправляю сигнал")
    event.set()


t1 = threading.Thread(target=waiter)
t2 = threading.Thread(target=signaler)
t1.start()
t2.start()
t1.join()
t2.join()