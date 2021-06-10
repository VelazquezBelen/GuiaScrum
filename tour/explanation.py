from typing import List


class Explanation:
    def __init__(self, name: List):
        self._name = name
        self._detail_level = 0

    @property
    def name(self):
        return self._name[0]    # Returns the explanation with less detail

    @property
    def tema(self):
        action = self._name[0]
        return action[6:].replace("_"," ")    # Returns the tema of the explanation 
        
    @property
    def next_detail_level(self):
        self._detail_level += 1
        if self._detail_level >= len(self._name):   # If I gave the user all the possible explanations
            return self._name[len(self._name)-1]    # I repeat the explanation that has more details.
        else: return self._name[self._detail_level] # Otherwise i give him the explanation with more detail.
