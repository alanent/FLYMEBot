# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from booking_details import BookingDetails

class Intent(Enum):
    BOOK_FLIGHT = "BookFlight"
    NONE_INTENT = "None"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0
    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score
    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(luis_recognizer: LuisRecognizer, turn_context: TurnContext) -> (Intent, object):
        result = None
        intent = None
        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)
            intent = (
                sorted(recognizer_result.intents, key=recognizer_result.intents.get, reverse=True)[:1][0]

                if recognizer_result.intents
                else None)

            if intent == Intent.BOOK_FLIGHT.value:
                result = BookingDetails()

                or_entities = recognizer_result.entities.get("$instance", {}).get("or_city", [])
                if len(or_entities) > 0:
                    result.origin = or_entities[0]["text"].capitalize()
                
                dst_entities = recognizer_result.entities.get("$instance", {}).get("dst_city", [])
                if len(dst_entities) > 0:
                    result.destination = dst_entities[0]["text"].capitalize()

                datetime_start = None
                datetime_end = None
                date_entities = recognizer_result.entities.get("datetime", {})
                if date_entities:
                    if len(date_entities) > 0:
                        timex = date_entities[0]["timex"]
                        if date_entities[0]["type"] == "daterange":
                            datetime_value = timex[0].replace("(", "").replace(")", "").split(",")
                            datetime_start = datetime_value[0]
                            datetime_end = datetime_value[1]
                        elif date_entities[0]["type"] == "date":
                            datetime_start = timex[0]
                result.start_date = datetime_start
                result.end_date = datetime_end
       
                budget_entities = recognizer_result.entities.get("$instance", {}).get("budget", [])
                if len(budget_entities) > 0:
                    result.budget = budget_entities[0]["text"]
        
        except Exception as exception:
            print(exception)

        return intent, result