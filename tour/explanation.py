from typing import List


class Explanation:
    def __init__(self, name: List):
        self._name = name
        self._detail_level = 0

    @property
    def name(self):
        return self._name[0]    # returns the explanation with less detail
        
    @property
    def next_detail_level(self):
        self._detail_level += 1
        return self._name[self._detail_level]
