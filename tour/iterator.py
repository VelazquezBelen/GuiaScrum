import abc
from typing import Dict, List

from tour.explanation import Explanation


class Iterator(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def next(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, intent: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def re_explain(self) -> str:
        pass


class BasicIterator(Iterator):

    def __init__(
            self,
            explanations: List[Explanation],
            intents: Dict[str, str]
    ):
        # Explain order.
        self._explain_order: List[Explanation] = []
        # Position in the defined explain order.
        self._current_pos = 0
        # Last explanation given to the user.
        self._last_explanation: Explanation = None
        # Explanations data.
        self._explanations: Dict[str, Explanation] = {}
        # Dict {k: v}, where k is a intent name, and v is the corresponding
        # explanation to give.
        self._intents = intents
        keys = list(self._intents.keys())
        for i in range(0,len(keys)):
            self._explanations[keys[i]] = explanations[i]
            self._explain_order.append(explanations[i])       

    def next(self) -> str:
        if self._current_pos == len(self._explain_order): # The tour ended
            return 'utter_goodbye'
        explanation = self._explain_order[self._current_pos]
        self._current_pos += 1
        self._last_explanation = explanation
        return explanation.name

    def get(self, intent_name: str) -> str:
        explanation = self._intents[intent_name]
        self._last_explanation = explanation
        return explanation

    def re_explain(self) -> str:
        # Explain with one more level of detail.
        return self._last_explanation.next_detail_level
