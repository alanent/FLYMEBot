# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from botbuilder.dialogs import (ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.schema import InputHints, Attachment
import json, re
from booking_details import BookingDetails
from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper, Intent
from .booking_dialog import BookingDialog

class MainDialog(ComponentDialog):
    
    def __init__(
        self,
        luis_recognizer: FlightBookingRecognizer,
        booking_dialog: BookingDialog,
        telemetry_client: BotTelemetryClient = None):
        super(MainDialog, self).__init__(MainDialog.__name__)
        self.telemetry_client = telemetry_client or NullTelemetryClient()
        self._luis_recognizer = luis_recognizer
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = self.telemetry_client
        self.add_dialog(text_prompt)
        booking_dialog.telemetry_client = self.telemetry_client
        self.add_dialog(booking_dialog)
        self._booking_dialog_id = booking_dialog.id
        wf_dialog = WaterfallDialog(
            "WFDialog", [self.intro_step, self.act_step, self.final_step])
        wf_dialog.telemetry_client = self.telemetry_client
        self.add_dialog(wf_dialog)
        self.initial_dialog_id = "WFDialog"

   
    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input))
            return await step_context.next(None)
        msg = (
            str(step_context.options)
            if step_context.options
            else "What is your next trip ?")
        prompt_message = MessageFactory.text(msg, msg, InputHints.expecting_input)
        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message))
   

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            # LUIS is not configured, we just run the BookingDialog path with an empty BookingDetailsInstance.
            return await step_context.begin_dialog(self._booking_dialog_id, BookingDetails())

        # Call LUIS and gather any potential booking details. (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await LuisHelper.execute_luis_query(self._luis_recognizer, step_context.context)
        if intent == Intent.BOOK_FLIGHT.value and luis_result:
            # Run the BookingDialog giving it whatever details we have from the LUIS call.
            return await step_context.begin_dialog(self._booking_dialog_id, luis_result)
        else:
            didnt_understand_msg = ("Sorry, I didn't get that. Please try asking in a different way")
            didnt_understand_message = MessageFactory.text(
                didnt_understand_msg, didnt_understand_msg, InputHints.ignoring_input)
            await step_context.context.send_activity(didnt_understand_message)
        return await step_context.next(None)

    
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result is not None:
            result = step_context.result
        prompt_message = "What else can I do for you?"
        return await step_context.replace_dialog(self.id, prompt_message)

    
    # Create internal function
    def replace(self, templateCard: dict, data: dict):
        string_temp = str(templateCard)
        for key in data:
            pattern = "\${" + key + "}"
            string_temp = re.sub(pattern, str(data[key]), string_temp)
        return eval(string_temp)

