from typing import List, Callable, Tuple, Any, Type, Union
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

class Item:
    def __init__(self, name: str, prev_item: Type['Item']=None):
        self.__name: str = name
        self.__prev: Item = prev_item
        self.__next: List[Item] = []
        self.__actions: List[Tuple[Callable,Union[Tuple[Any],List[Any]]]] = []
        self.__is_empty = True
                
    def add_next_item(self, name: str):
        item = Item(name, self)
        self.__next.append(item)
        self.__is_empty = False
        return item
    
    def add_action(self, function: Callable, params: Union[Tuple[Any],List[Any]]=[]):
        self.__actions.append((function, params))
    
    def get_name(self):
        return self.__name
    
    def get_prev_item(self):
        return self.__prev
        
    def get_next_items(self) -> List[Type['Item']]:
        return self.__next

    def get_actions(self) -> List[Tuple[Callable,Union[Tuple[Any],List[Any]]]]:
        return self.__actions

    def is_empty(self):
        return self.__is_empty
        
        
class Navigator:
    def __init__(self, start_item: Item, back_button_name: str=None):
        self.__start_item = start_item
        self.__current_item = start_item
        self.__keyboard = None
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
    
    def __run_actions(self) -> List[Any]:
        actions = self.__current_item.get_actions()
        # print("In run_actions function: Current_item_name:", self.__current_item.get_name())
        # print("In run_actions function: list of actions:", actions)
        self.__results_buffer = []
        for action in actions:
            function, args = action
            result = function(*args)
            # print("Result:",result)
            self.__results_buffer.append(result)
        return self.__results_buffer
        
    def goto(self, name: str) -> Tuple[bool, List[Any]]:
        results: Tuple[bool, List[Any]] = (None, None)
        next_items = self.__current_item.get_next_items()
        if name == self.__back_button_name:
            results = self.__go_back(True)
            return results
        for next_item in next_items:
            if next_item.get_name() == name:
                self.__current_item = next_item
                results = self.__run_actions()
                if next_item.is_empty():
                    results = self.__go_back(False)
                    return results
                results = (True, results)
                return results
        results = (False, [])
        return results
    
    def __go_back(self, is_changed: bool):
        if not self.__current_item.get_prev_item():
            self.__current_item = self.__start_item
        else:
            self.__current_item = self.__current_item.get_prev_item()
        return (is_changed, [])
