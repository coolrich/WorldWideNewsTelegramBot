from typing import List, Callable, Tuple, Any, Type, Union
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message
from abc import ABC, abstractmethod

class Action(ABC):
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        pass
        
class Item:
    def __init__(self, name: str, prev_item: Type['Item']=None):
        self.__name: str = name
        self.__prev: Item = prev_item
        self.__next: List[Item] = []
        self.__actions: List[Action] = []
        self.__is_empty = True
                
    def add_next_item(self, name: str):
        item = Item(name, self)
        self.__next.append(item)
        self.__is_empty = False
        return item
    
    def add_action(self, action: Action):
        self.__actions.append(action)
    
    def get_name(self):
        return self.__name
    
    def get_prev_item(self):
        return self.__prev
        
    def get_next_items(self) -> List[Type['Item']]:
        return self.__next

    def get_actions(self) -> List[Action]:
        return self.__actions

    def is_empty(self):
        return self.__is_empty
        
    def __getstate__(self):
        return {
        "name" : self.__name,
        "prev" : self.__prev,
        "next" : self.__next,
        "actions" : [],#self.__actions,
        "is_empty" : self.__is_empty,
        }

    def __setstate__(self, state):
        self.__name = state["name"]
        self.__prev = state["prev"]
        self.__next = state["next"]
        self.__actions = []#state["actions"]
        self.__is_empty = state["is_empty"]
        
class Navigator:
    def __init__(self, start_item: Item, back_button_name: str=None):
        self.__start_item = start_item
        self.__current_item = start_item
        self.__back_button_name = back_button_name
        self.__results_buffer: List[Any] = []
        self.__run_actions()
        
    def get_keyboard(self):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        next_items = self.__current_item.get_next_items()
        for next_item in next_items:
            keyboard.add(next_item.get_name())
        if self.__back_button_name and self.__current_item.get_name() != self.__start_item.get_name():
            keyboard.add(self.__back_button_name)
        return keyboard
    
    def get_item_name(self):
        return self.__current_item.get_name()
    
    def get_results_buffer(self):
        return self.__results_buffer
    
    def __run_actions(self, message: Message=None) -> List[Any]:
        actions = self.__current_item.get_actions()
        self.__results_buffer = []
        for action in actions:
            if message:
                result = action.run(message=message)
            self.__results_buffer.append(result)
        return self.__results_buffer
        
    def goto(self, message: Message) -> Tuple[bool, List[Any]]:
        name: str = message['text']
        results: List[Any] = []
        next_items = self.__current_item.get_next_items()
        is_changed = False
        if name == self.__back_button_name:
            is_changed = self.__go_back(True)
            return (is_changed, results)
        for next_item in next_items:
            if next_item.get_name() == name:
                self.__current_item = next_item
                results = self.__run_actions(message)
                if self.__current_item.is_empty():
                    is_changed = self.__go_back(False)
                    return (is_changed, results)
                is_changed = True
                return (is_changed, results)
        return (False, results)
    
    def __go_back(self, is_changed: bool):
        if not self.__current_item.get_prev_item():
            self.__current_item = self.__start_item
        else:
            self.__current_item = self.__current_item.get_prev_item()
        return is_changed
        
    def __getstate__(self):
        return {
        "start_item" : self.__start_item,
        "current_item" : self.__current_item,
        "back_button_name" : self.__back_button_name,
        # "results_buffer" : self.__results_buffer,
        }

    def __setstate__(self, state):
        self.__start_item = state["start_item"]
        self.__current_item = state["current_item"]
        self.__back_button_name = state["back_button_name"]
        # self.__results_buffer = state["results_buffer"]
