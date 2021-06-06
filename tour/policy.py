import json
from typing import Any, List, Dict, Text, Optional

from rasa.core.featurizers.tracker_featurizers import TrackerFeaturizer
from rasa.core.policies.policy import PolicyPrediction, confidence_scores_for, \
    Policy
from rasa.shared.core.domain import Domain
from rasa.shared.core.generator import TrackerWithCachedStates
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.nlu.interpreter import NaturalLanguageInterpreter

from tour import iterator
from tour.explanation import Explanation
from tour.event_handling import EventPublisher

publisher = EventPublisher("log_eventos")

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
    if response == "utter_greet":
        publisher.publish("movement",
            {"location" : "recorridoAsistenteScrum_punto1",          
                "to": "Cristina"})
    if response == "utter_product_backlog" or response == "utter_sprint_backlog":
        publisher.publish("movement",
                    {"location" : "recorridoAsistenteScrum_punto2",
                    "to": "Cristina"})
    if response == "utter_scrum_master":
        publisher.publish("movement",
                {"location" : "recorridoAsistenteScrum_punto3",
                "to": "Cristina"})
    if response == "utter_scrum_board":
        publisher.publish("movement",
                {"location" : "recorridoAsistenteScrum_punto4",
                "to": "Cristina"})
    if response == "utter_development_team":
        publisher.publish("movement",
                {"location" : "recorridoAsistenteScrum_punto5",
                "to": "Cristina"})
    if response == "utter_daily_meeting":
                publisher.publish("movement",
                {"location" : "recorridoAsistenteScrum_punto5",
                "to": "Cristina"})

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
            r"info\explanations.json",
            r"info\intents.json"
        )

        self._route = {"utter_greet" : "recorridoAsistenteScrum_punto1",
                    "utter_product_backlog" : "recorridoAsistenteScrum_punto2",
                    "utter_sprint_backlog" : "recorridoAsistenteScrum_punto2",
                    "utter_scrum_master" : "recorridoAsistenteScrum_punto3",
                    "utter_scrum_board" : "recorridoAsistenteScrum_punto4",
                    "utter_development_team" : "recorridoAsistenteScrum_punto5",
                    "utter_daily_meeting" : "recorridoAsistenteScrum_punto6"}  ### ver si este esta bien
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
                move_to_a_location("utter_greet")
                return self._prediction(confidence_scores_for('utter_greet', 1.0, domain
                ))
            # The user wants to continue with next explanation.
            if intent["name"] == "affirm":
                response = self._it.next()
                move_to_a_location(response)
                return self._prediction(confidence_scores_for(
                    response, 1.0, domain
                ))
            # The user didn't understand and needs a re explanation.
            if intent["name"] == "no_entiendo" or intent["name"] == "deny":
                return self._prediction(confidence_scores_for(
                    self._it.re_explain(), 1.0, domain
                ))
            # The user wants an explanation of a specific topic.
            return self._prediction(confidence_scores_for(
                self._it.get(intent["name"]), 1.0, domain
            ))
            

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

