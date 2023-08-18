
import math
import operator
import sys


import copy
from rpython.rlib.objectmodel import specialize
from rpython.rlib import jit
from rpython.rlib.objectmodel import (
    import_from_mixin, instantiate, newlist_hint, resizelist_hint, specialize)
from rpython.rlib.rarithmetic import ovfcheck
from rpython.rlib import jit, objectmodel, rerased, rarithmetic

class W_TableObject:
    contain_typed = None
    tabOne = None
    tabTwo = None
    tabThree = None
    size = 0
    map_dict = {}
    
    def get_type(self):   
        print("type", self.contain_typed) 
                 
    def split_list(self, w_vector, new_strategy, list_w, hint, index0= -1):
        self.tabOne = w_vector
        copied = copy.deepcopy(w_vector)
        lst = w_vector.get_strategy()._storage(w_vector)
        print("UN LIST", lst)
        del lst[index0]
        lst_w = [w_vector.get_strategy().wrap(i) for i in lst]
        storage = w_vector.get_strategy().create_storage_for_elements(lst_w)
        self.tabOne.set_storage(storage)
        for i, item in enumerate(list_w):
            if i is index0:
                self.map_dict[self.size] = ('tabTwo', 0) 
                self.size+=1
            else:
                self.map_dict[self.size] = ('tabOne', i) 
                self.size+=1
        self.tabTwo = copied
        storage = new_strategy.create_storage_for_element(hint, 1)
        self.tabTwo.set_strategy(new_strategy)
        self.tabTwo.set_storage(storage)
        print("TABLE ONE", self.tabOne.get_strategy()._storage(self.tabOne))
        print("TABLE TWO", self.tabTwo.get_strategy()._storage(self.tabTwo))
        print("maping0", self.map_dict)
        self.map_dict = self.update_map("tabOne")
        print("maping", self.map_dict)
        print("TABLE", self.tabTwo.table, self.tabOne.table)

    def split_hash(self, w_dict, w_key, w_val):
        # keys = [w_dict.strategy.wrap(key) for key in dict_w.keys()]
        # values = dict_w.values()
        self.tabOne = w_dict
        # w_dict.is_immutable = False
        self.tabTwo = w_dict.make_empty()
        self.tabTwo._set(w_key, w_val)
        
        print("tabon hash", self.tabOne.strategy.unerase(self.tabOne.hstorage))

        print("tabtwo hash", self.tabTwo.strategy.unerase(self.tabTwo.hstorage))

    def get_storage_hash(self):
        return self.tabOne.strategy.unerase(self.tabOne.hstorage).update(self.tabTwo.strategy.unerase(self.tabTwo.hstorage))

    def get(w_key, w_missing = None):
        if self.tabOne.strategy.is_correct_type(w_key):
            key = self.tabOne.strategy.unwrap(w_key)
        else:
            key = self.tabTwo.strategy.unwrap(w_key)
        return self.get_storage_hash().get(key, w_missing)

        
    def append(self, list_w):
        for i in range(len(list_w)):
            if self.tabOne.strategy._check_can_handle(list_w[i]):
                self.tabOne.strategy.get_storage(self.tabOne).append(self.tabOne.strategy.unwrap(list_w[i]))
                self.map_dict[self.size] = ('tabOne', self.tabOne.strategy.get_storage(self.tabOne).index(self.tabOne.strategy.unwrap(list_w[i])))
            elif self.tabTwo.strategy._check_can_handle(list_w[i]):
                self.tabTwo.strategy.get_storage(self.tabTwo).append(self.tabTwo.strategy.unwrap(list_w[i]))
                self.map_dict[self.size] = ('tabTwo', self.tabTwo.strategy.get_storage(self.tabTwo).index(self.tabTwo.strategy.unwrap(list_w[i])))
            else:   
                if self.tabThree is None:
                    strategy_type2 = self.tabOne.strategy.generalized_strategy_table(list_w[i])
                    copied = copy.deepcopy(self.tabTwo)
                    strategy = self.tabTwo.strategy.strategy_factory().switch_strategy_table(copied, strategy_type2)
                    strategy.append(copied, list_w)
                    self.tabThree = copied
                    self.map_dict[self.size] = ('tabThree', 0) 
                else:
                    self.tabThree.strategy.get_storage(self.tabThree).append(self.tabThree.strategy.unwrap(list_w[i]))
                    self.map_dict[self.size] = ('tabThree', self.tabThree.strategy.get_storage(self.tabThree).index(self.tabThree.strategy.unwrap(list_w[i])))
            self.size+=1
        if self.tabOne:
            print("tabOne", self.tabOne.strategy.get_storage(self.tabOne))
        if self.tabTwo:
            print("tabTwo", self.tabTwo.strategy.get_storage(self.tabTwo))
        if self.tabThree:
            print("tabThree", self.tabThree.strategy.get_storage(self.tabThree))

    
    def _reverse_map(self):
        reversed_dict = {}
        for key, value in self.map_dict.items():
            reversed_dict.setdefault(value, []).append(key)
        # Find keys that have the same values
        keys_with_same_values = [keys for keys in reversed_dict.values() if len(keys) > 1]
        rev = keys_with_same_values[::-1]
        return keys_with_same_values

    def modify_map(self, index):
        new_dict = {}
        for key, value in self.map_dict.items():
            new_key = key + 1 if key >= index else key
            new_dict[new_key] = value
        return new_dict
    
    def reverse(self):
        k = list(self.map_dict.keys())
        v = list(self.map_dict.values())
        x = len(k) -1
        for i in range(len(k)):
            self.map_dict[k[x-i]] = v[i]
            
    def reversed_map(self, _dict):
        dct = _dict
        keys = list(dct.keys())
        values = list(dct.values())
        keys.reverse()
        values.reverse()
        result_dict = {keys[i]: values[i] for i in range(min(len(keys), len(values)))}
        result_dict = dict(zip(keys, values))
        return result_dict


    def incre_map(self, index):
        filtered_list = [item for item in self.map_dict if item > index]

        return filtered_list

    def insert(self, index0, list_w):
        if index0 >= self.length():
            index0 = self.length()-1
        try:
            res = self.map_dict[index0]
            index = res[1]
        except KeyError:
            raise IndexError("error in insert table")
        a = self.getitem(index0)
        w_a = self.wrap(a, index0)
        x = self.map_dict[index0]
        w = self.map_dict[index0]
        self.map_dict =  self.modify_map(index0)
        if self.tabOne.strategy._check_can_handle(list_w[0]):
            # self.tabOne.strategy.insert(self.tabOne, index0, list_w)
            if self.tabOne.strategy._check_can_handle(w_a):
                self.tabOne.strategy.get_storage(self.tabOne).insert(index, self.tabOne.strategy.unwrap(list_w[0]))
                self.map_dict[index0] = ('tabOne', self.tabOne.strategy.get_storage(self.tabOne).index(self.tabOne.strategy.unwrap(list_w[0])))
                h = self.map_dict[self.size]
                self.map_dict[self.size] = ('tabOne', self.tabOne.strategy.get_storage(self.tabOne).index(a))
                self.map_dict[self.size] = h
                
                for i in range(self.length()):
                    for item in self._reverse_map():
                        mx = max(item)
                        mx_val = self.map_dict[mx]
                        self.map_dict[mx] = (mx_val[0], mx_val[1]+1)
            elif self.tabTwo.strategy._check_can_handle(w_a):
                self.tabOne.strategy.get_storage(self.tabOne).insert(index, self.tabOne.strategy.unwrap(list_w[0]))
                self.map_dict[index0] = ('tabOne', self.tabOne.strategy.get_storage(self.tabOne).index(self.tabOne.strategy.unwrap(list_w[0])))
                h = self.map_dict[self.size]
                self.map_dict[self.size] = ('tabTwo', self.tabTwo.strategy.get_storage(self.tabTwo).index(a))
                self.map_dict[self.size] = h
                for i in range(self.length()):
                    for item in self._reverse_map():
                        mx = max(item)
                        mx_val = self.map_dict[mx]
                        self.map_dict[mx] = (mx_val[0], mx_val[1]+1)
            else:
                self.tabOne.strategy.get_storage(self.tabOne).insert(index, self.tabOne.strategy.unwrap(list_w[0]))
                self.map_dict[index0] = ('tabOne', self.tabOne.strategy.get_storage(self.tabOne).index(self.tabOne.strategy.unwrap(list_w[0])))
                h = self.map_dict[self.size]
                self.map_dict[self.size] = ('tabThree', self.tabThree.strategy.get_storage(self.tabThree).index(a))
                self.map_dict[self.size] = h
                for i in range(self.length()):
                    for item in self._reverse_map():
                        mx = max(item)
                        mx_val = self.map_dict[mx]
                        self.map_dict[mx] = (mx_val[0], mx_val[1]+1)

        elif self.tabTwo.strategy._check_can_handle(list_w[0]):
            self.tabTwo.strategy.get_storage(self.tabTwo).insert(index, self.tabTwo.strategy.unwrap(list_w[0]))
            # self.tabTwo.strategy.insert(self.tabTwo, index0, list_w)
            self.map_dict[index0] = ('tabTwo', self.tabTwo.strategy.get_storage(self.tabTwo).index(self.tabTwo.strategy.unwrap(list_w[0])))
            y = self.map_dict[self.size]
            if self.tabOne.strategy._check_can_handle(w_a):
                self.map_dict[self.size] = ('tabOne', self.tabOne.strategy.get_storage(self.tabOne).index(a))
                self.map_dict[self.size] = y

            elif self.tabTwo.strategy._check_can_handle(w_a):
                self.map_dict[self.size] = ('tabTwo', self.tabTwo.strategy.get_storage(self.tabTwo).index(a))
                self.map_dict[self.size] = y
            else:
                self.map_dict[self.size] = ('tabThree', self.tabThree.strategy.get_storage(self.tabThree).index(a))
                self.map_dict[self.size] = y
            for i in range(self.length()):
                for item in self._reverse_map():
                    mx = max(item)
                    mx_val = self.map_dict[mx]
                    self.map_dict[mx] = (mx_val[0], mx_val[1]+1)
        
        else:
            self.tabThree.strategy.get_storage(self.tabThree).insert(index, self.tabThree.strategy.unwrap(list_w[0]))
            # self.tabTwo.strategy.insert(self.tabTwo, index0, list_w)
            self.map_dict[index0] = ('tabThree', self.tabThree.strategy.get_storage(self.tabThree).index(self.tabThree.strategy.unwrap(list_w[0])))
            y = self.map_dict[self.size]
            if self.tabOne.strategy._check_can_handle(w_a):
                self.map_dict[self.size] = ('tabOne', self.tabOne.strategy.get_storage(self.tabOne).index(a))
                # self.map_dict[self.size] = x
                self.map_dict[self.size] = y

            elif self.tabTwo.strategy._check_can_handle(w_a):
                self.map_dict[self.size] = ('tabTwo', self.tabTwo.strategy.get_storage(self.tabTwo).index(a))
                # self.map_dict[self.size] = x
                self.map_dict[self.size] = y
            else:
                self.map_dict[self.size] = ('tabThree', self.tabThree.strategy.get_storage(self.tabThree).index(a))
                # self.map_dict[self.size] = x
                self.map_dict[self.size] = y
            for i in range(self.length()):
                for item in self._reverse_map():
                    mx = max(item)
                    mx_val = self.map_dict[mx]
                    self.map_dict[mx] = (mx_val[0], mx_val[1]+1)
        

        self.size+=1

        if self.tabOne:
            print("tabOne", self.tabOne.strategy.get_storage(self.tabOne))
        if self.tabTwo:
            print("tabTwo", self.tabTwo.strategy.get_storage(self.tabTwo))

    def storage(self):
        storage = []
        if self.tabOne:
            storage.extend(self.tabOne.get_strategy()._storage(self.tabOne))
        if self.tabTwo:
            storage.extend(self.tabTwo.get_strategy()._storage(self.tabTwo))
        if self.tabThree:
            storage.extend(self.tabThree.get_strategy()._storage(self.tabThree))
        return storage
    
    def get_storage(self):
        storage = []
        for i in range(self.length()):
            storage.append(self.getitem(i))
        return storage

    def getitem(self, index):
        try:
            pos = self.map_dict
            res = pos[index]
            if res[0] == 'tabOne':
                return self.tabOne.get_strategy()._storage(self.tabOne)[res[1]]
            if res[0] == 'tabTwo':
                return self.tabTwo.get_strategy()._storage(self.tabTwo)[res[1]]
            else:
                return self.tabThree.get_strategy()._storage(self.tabThree)[res[1]]
        except KeyError:
            raise IndexError("in table getitem")
  

    def length(self):
        return len(self.storage())

    def wrap(self, value, index):
        try:
            pos = self.map_dict
            res = pos[index]
            if res[0] == 'tabOne':
                return self.tabOne.strategy.wrap(value)
            elif res[0] == 'tabTwo':
                return self.tabTwo.strategy.wrap(value)
            else:
                return self.tabThree.strategy.wrap(value)    
        except KeyError:
            raise IndexError("in table wrap method")

    def store(self, index0, wrapped_value):
        removed = self.getitem(index0)
        w_removed = self.wrap(removed, index0)
        if self.tabOne.strategy.is_correct_type(self.tabOne, w_removed):
            self.tabOne.strategy._storage(self.tabOne).pop(self.tabOne.strategy._storage(self.tabOne).index(removed))
            self.size-=1
        elif self.tabTwo.strategy.is_correct_type(self.tabTwo, w_removed):
            self.tabTwo.strategy._storage(self.tabTwo).pop(self.tabTwo.strategy._storage(self.tabTwo).index(removed))
            self.size-=1
        else:
            self.tabThree.strategy.get_storage(self.tabThree).pop(self.tabThree.strategy.get_storage(self.tabThree).index(removed))
            self.size-=1
        
        if self.tabOne.strategy.is_correct_type(self.tabOne, wrapped_value):
            y = [i for i in self.map_dict.keys() if self.map_dict[i][0] == "tabOne"]
            print("CHECK", y, index0, self.tabOne.strategy._storage(self.tabOne), self.map_dict)
            if index0 >= max(y):
                self.tabOne.strategy._storage(self.tabOne).insert(index0, self.tabOne.strategy.unwrap(wrapped_value))
            else:
                self.tabOne.strategy._storage(self.tabOne).insert((len(self.tabOne.strategy._storage(self.tabOne))-1), self.tabOne.strategy.unwrap(wrapped_value))
            self.map_dict[index0] = ('tabOne', self.tabOne.strategy._storage(self.tabOne).index(self.tabOne.strategy.unwrap(wrapped_value)))
        elif self.tabTwo.strategy.is_correct_type(self.tabTwo, wrapped_value):
            y = [i for i in self.map_dict.keys() if self.map_dict[i][0] == "tabTwo"]
            if index0 >= max(y):
                self.tabTwo.strategy._storage(self.tabTwo).insert(index0, self.tabTwo.strategy.unwrap(wrapped_value))
            else:
                self.tabTwo.strategy._storage(self.tabTwo).insert((len(self.tabTwo.strategy._storage(self.tabTwo))-1), self.tabTwo.strategy.unwrap(wrapped_value))
            self.map_dict[index0] = ('tabTwo', self.tabTwo.strategy._storage(self.tabTwo).index(self.tabTwo.strategy.unwrap(wrapped_value)))
        else: 
            if self.tabThree is None:
                self.tabThree = self.tabTwo.fromelements([wrapped_value])
                self.map_dict[index0] = ('tabThree', 0) 
            else:
                y = [i for i in self.map_dict.keys() if self.map_dict[i][0] == "tabTwo"]
                if index0 >= max(y):
                    self.tabThree.strategy._storage(self.tabThree).insert(index0, self.tabTwo.strategy.unwrap(wrapped_value))
                else:
                    self.tabThree.strategy._storage(self.tabThree).insert((len(self.tabThree.strategy._storage(self.tabThree))-1), self.tabThree.strategy.unwrap(wrapped_value))
                self.map_dict[index0] = ('tabThree', self.tabThree.strategy.get_storage(self.tabThree).index(self.tabThree.strategy.unwrap(wrapped_value)))
        self.size+=1
        
        self.map_dict = self.update_map('tabOne')
        self.map_dict = self.update_map('tabTwo')
        self.map_dict = self.update_map('tabThree')
        if self.tabOne:
            print("tabOne", self.tabOne.strategy._storage(self.tabOne))
        if self.tabTwo:
            print("tabTwo", self.tabTwo.strategy._storage(self.tabTwo))
        if self.tabThree:
            print("tabThree", self.tabThree.strategy._storage(self.tabThree))
    
    def update_map(self, table):
        updated_dict = {}
        tab_two_counter = 0
        for key, value in self.map_dict.items():
            if value[0] == table:
                updated_value = (value[0], tab_two_counter)
                tab_two_counter += 1
            else:
                updated_value = value
            updated_dict[key] = updated_value

        return updated_dict

    def delete(self, start, end):
        storage = {}
        if end > self.length():
            end = self.length()
        for i in range(start, end):
            storage[i] = self.getitem(i)
        w_storage = [self.wrap(removed, i) for i,removed in storage.items()]
        for i in range(len(w_storage)):
            if self.tabOne.strategy._check_can_handle(w_storage[i]):
                start = self.tabOne.strategy.get_storage(self.tabOne).index(self.tabOne.strategy.unwrap(w_storage[i]))
                # self.tabOne.strategy.delete(self.tabOne, start, start+1)
                del self.tabOne.strategy.get_storage(self.tabOne)[start:start+1]
            elif self.tabTwo.strategy._check_can_handle(w_storage[i]):
                start = self.tabTwo.strategy.get_storage(self.tabTwo).index(self.tabTwo.strategy.unwrap(w_storage[i]))
                # self.tabTwo.strategy.delete(self.tabTwo, start, start+1)
                del self.tabTwo.strategy.get_storage(self.tabTwo)[start:start+1]
            else:
                start = self.tabThree.strategy.get_storage(self.tabThree).index(self.tabThree.strategy.unwrap(w_storage[i]))
                # self.tabTwo.strategy.delete(self.tabTwo, start, start+1)
                del self.tabThree.strategy.get_storage(self.tabThree)[start:start+1]
            self.size-=1
        for index in storage:
            del self.map_dict[index]
        del storage

        consecutive_dict = {}
        new_key = 0
        for key, value in self.map_dict.items():
            while new_key in consecutive_dict:
                new_key += 1
            consecutive_dict[new_key] = value
            new_key += 1 
        self.map_dict = consecutive_dict

        self.map_dict = self.update_map('tabOne')
        self.map_dict = self.update_map('tabTwo')
        self.map_dict = self.update_map('tabThree')

