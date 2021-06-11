import abc
from typing import Dict, List
from tour import explanation
from rasa.shared.core.events import SlotSet

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
        self._last_explanation = None 
        # Explanations data (The explanations in the tour, in order).
        self._explanations = explanations
        # The intents with their corresponding response.
        self._intents = intents

    def next(self) -> str:
        if self._current_pos == len(self._explanations): # The tour ended
            return 'utter_end_tour'
        explanation = self._explanations[self._current_pos]
        self._current_pos += 1
        self._last_explanation = explanation
        return explanation.name

    def get(self, intent_name: str, tracker) -> str:
        explanation = self._intents[intent_name]
        # The user asks for an explanation that is the next explanation in the tour
        if(self._explanations[self._current_pos].name) == explanation:
            self.next()

        # If the user asks for an explanation that will be given later in the tour,
        # i give him a preview.
        for i in range(self._current_pos+1, len(self._explanations)):
            if self._explanations[i].name == explanation:
                # Set the slot 'tema' with the tema of the actual explanation
                tracker.update(SlotSet("tema", self._explanations[self._current_pos].tema))
                return explanation + '_preview'

        # Otherwise i give him the complete answer.
        # (No guardo la explicación en last_explanation porque las explicaciones que no están 
        # en el tour no tienen otra explicación con mas detalle.)      
        return explanation                                        

    def re_explain(self) -> str:
        # Explain with one more level of detail.
        return self._last_explanation.next_detail_level

    def reset_tour(self):
        self._current_pos = 0
