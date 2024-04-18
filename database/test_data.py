from database.models import *
from typing import Dict

test_events: Dict[int, Event] = {}

start_event = Event(1010, "У вашего босса случился припадок, вы единственный свидетель, и только вы можете спасти грядущий релиз", 
                     actions=[
                         Action(1, "Упасть в обморок", price=-20, next_event_id=1011),
                         Action(2, "Переодеться в босса", price=60, next_event_id=1012),
                         Action(3, "Нажать красную кнопку отложить релиз", price=210, next_event_id=1016),
                         ])

event1011 = Event(1011, "Ваш босс умер", 
                     actions=[
                         Action(1, "Уволиться", price=0, next_event_id=None),
                         Action(2, "Вздохнуть и дописать свою фамилию в списке директоров", price=60, next_event_id=1015),
                         Action(3, "Нажать красную кнопку отложить релиз", price=210, next_event_id=1016),
                         ])



event1012 = Event(1012, "Начался зомби вирус", 
                     actions=[
                         Action(1, "Застрелиться", price=0, next_event_id=None),
                         Action(2, "Выпить кофе", price=-10, next_event_id=1017),
                         Action(3, "Сбилдить проект в андройд студио", price=-210, next_event_id=None),
                         ])

event1015 = Event(1015, "Теперь вы босс и первым вашим делом стал следующий указ", 
                     actions=[
                         Action(1, "Арендовать яндекс облако", price=-20, next_event_id=1020),
                         Action(2, "Уволить всех", price=-360, next_event_id=1018),
                         Action(3, "Уехать в отпуск", price=1210, next_event_id=1019),
                         ])

event1016 = Event(1016, "К вам в офис ворвался отряд ФСБ", 
                     actions=[
                         Action(1, "Сдаться", price=0, next_event_id=None),
                         Action(2, "Отбиваться телом босса", price=60, next_event_id=None),
                         Action(3, "Попытаться уехать на кресле", price=5, next_event_id=1019),
                         ])

event1017 = Event(
    1017,
    "В офисе началась эпидемия вируса 'программистский блок' и кофе не доступно. Что вы будете делать?",
    [
        Action(1, "Попить воды", price=-5, next_event_id=None),
        Action(2, "Начать заниматься йогой", price=-15, next_event_id=None),
        Action(3, "Сделать паузу и поиграть в компьютерные игры", price=-30, next_event_id=None),
    ]
)

event1018 = Event(
    1018,
    "Вы обнаружили, что весь ваш код был удален. Как вы реагируете?",
    [
        Action(1, "Начать паниковать", price=-20, next_event_id=None),
        Action(2, "Попытаться восстановить код из памяти", price=-40, next_event_id=None),
        Action(3, "Сделать перерыв и сходить за кофе", price=-10, next_event_id=None),
    ]
)

event1019 = Event(
    1019,
    "Вам удалось улизнуть из офиса, но отломалось колесико кресла",
    [
        Action(1, "Починить", price=-30, next_event_id=None),
        Action(2, "Побежать", price=20, next_event_id=None),
        Action(3, "Сдаться", price=0, next_event_id=None),
    ]
)

event1020 = Event(
    1020,
    "Вам предложили повышение, но с большей ответственностью. Как вы реагируете?",
    [
        Action(1, "Принять предложение", price=-100, next_event_id=None),
        Action(2, "Попросить больше времени на раздумье", price=0, next_event_id=None),
        Action(3, "Отказаться от предложения", price=50, next_event_id=None),
    ]
)

test_events[start_event.id] = start_event
test_events[event1011.id] = event1011
test_events[event1012.id] = event1012
test_events[event1015.id] = event1015
test_events[event1016.id] = event1016
test_events[event1017.id] = event1017
test_events[event1018.id] = event1018
test_events[event1019.id] = event1019
test_events[event1020.id] = event1020
