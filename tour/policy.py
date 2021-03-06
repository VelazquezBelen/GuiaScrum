import json
import os
from typing import Any, List, Dict, Text, Optional

from rasa.core.featurizers.tracker_featurizers import TrackerFeaturizer
from rasa.core.policies.policy import PolicyPrediction, confidence_scores_for, \
    Policy
from rasa.shared.core.domain import Domain, State
from rasa.shared.core.generator import TrackerWithCachedStates
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.nlu.interpreter import NaturalLanguageInterpreter

from tour import iterator
from tour.explanation import Explanation
from tour.event_handling import EventPublisher

from rasa.shared.core.events import SlotSet

publisher = EventPublisher("logistica_test")

def parse_raw_explanation(data: Dict[str, Any]) -> Explanation:
    return Explanation(list(data["name"]))

def _create_iterator(path_explanations: str, path_intents: str
                     ) -> iterator.Iterator:
    with open(path_explanations) as file:
        explanations = [parse_raw_explanation(e) for e in json.load(file)]
    with open(path_intents) as file:
        intents = json.load(file)
    return iterator.BasicIterator(explanations, intents)

def move_to_a_location(response):
    locations = {
        "utter_start_tour" : "tour_scrum_assistant_p1",
        "utter_move_to_sala_planning" : "tour_scrum_assistant_p2",
        "utter_move_to_sala_development": "tour_scrum_assistant_p5",
        "utter_move_to_sala_reuniones" : "tour_scrum_assistant_p6",
        "utter_move_to_tablero" : "tour_scrum_assistant_p4",
        "utter_move_to_oficina" : "tour_scrum_assistant_p3",
    }
    if locations.get(response) != None:
        publisher.publish("movement_now",
            {"location" : locations.get(response),
             "recipient": "Scrum Assistant"})  

def move_tarea(response):
    state = {
        "utter_tarea_in_progress" : "IN PROGRESS",
        "utter_tarea_done" : "TO DO"
    }
    if state.get(response) != None:
        publisher.publish("task",
        {"to" : "Scrum Assistant", 
        "action": "change_state", 
        "new_state": state.get(response), 
        "id_artefacto": "40"})

class TourPolicy(Policy):

    def __init__(
            self,
            featurizer: Optional[TrackerFeaturizer] = None,
            priority: int = 2,
            should_finetune: bool = False,
            **kwargs: Any
    ) -> None:
        super().__init__(featurizer, priority, should_finetune, **kwargs)
        
        self._it = _create_iterator(
            r"info" + os.path.sep + "explanations.json",
            r"info" + os.path.sep + "intents.json"
        )

    def train(
            self,
            training_trackers: List[TrackerWithCachedStates],
            domain: Domain,
            interpreter: NaturalLanguageInterpreter,
            **kwargs: Any
    ) -> None:
        pass

    def predict_action_probabilities(
            self,
            tracker: DialogueStateTracker,
            domain: Domain,
            interpreter: NaturalLanguageInterpreter,
            **kwargs: Any
    ) -> "PolicyPrediction":
        intent = tracker.latest_message.intent

        # If the last thing rasa did was listen to a user message, we need to
        # send back a response.
        if tracker.latest_action_name == "action_listen":
            # The user starts the conversation.
            if intent["name"] == "greet":
                tracker.update(SlotSet("next_topic", "utter_greet"))
                move_to_a_location("utter_greet")
                return self._prediction(confidence_scores_for('action', 1.0, domain
                ))
            if intent["name"] == "goodbye":
                tracker.update(SlotSet("next_topic", "utter_goodbye"))
                return self._prediction(confidence_scores_for('action', 1.0, domain
                ))
            # The user wants to continue with next explanation.
            if intent["name"] == "affirm":
                response = self._it.next()
                tracker.update(SlotSet("next_topic", response))
                move_to_a_location(response)
                move_tarea(response)
                if response == 'utter_end_tour': self._it.reset_tour()
                return self._prediction(confidence_scores_for(
                    'action', 1.0, domain
                ))
            # The user didn't understand and needs a re explanation.
            if intent["name"] == "no_entiendo" or intent["name"] == "deny":
                tracker.update(SlotSet("next_topic", self._it.re_explain()))
                return self._prediction(confidence_scores_for(
                    'action', 1.0, domain
                ))
            # The user needs an example.
            if intent["name"] == "ejemplo":
                tracker.update(SlotSet("next_topic",  self._it.get_example()))
                return self._prediction(confidence_scores_for(
                   'action', 1.0, domain
                ))
            # The bot did not understand the user.
            if intent["name"] == "nlu_fallback":
                tracker.update(SlotSet("next_topic", "utter_default"))
                return self._prediction(confidence_scores_for(
                   'action' , 1.0, domain
                ))
            # The user wants an explanation of a specific topic.
            tracker.update(SlotSet("next_topic",self._it.get(intent["name"],tracker)))
            return self._prediction(confidence_scores_for('action', 1.0, domain))

        # If rasa latest action isn't "action_listen", it means the last thing
        # rasa did was send a response, so now we need to listen again so the
        # user can talk to us.
        return self._prediction(confidence_scores_for(
            "action_listen", 1.0, domain
        ))

    def _metadata(self) -> Dict[Text, Any]:
        return {
            "priority": 2
        }

    @classmethod
    def _metadata_filename(cls) -> Text:
        return "tour_policy.json"