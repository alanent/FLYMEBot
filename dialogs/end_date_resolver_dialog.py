# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datatypes_date_time.timex import Timex
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.dialogs import WaterfallDialog, DialogTurnResult, WaterfallStepContext
from botbuilder.dialogs.prompts import (DateTimePrompt, PromptValidatorContext, PromptOptions, DateTimeResolution)
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog

class EndDateResolverDialog(CancelAndHelpDialog):

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient()):
        super(EndDateResolverDialog, self).__init__(dialog_id or EndDateResolverDialog.__name__, telemetry_client)
        self.telemetry_client = telemetry_client
        date_time_prompt = DateTimePrompt(DateTimePrompt.__name__, EndDateResolverDialog.datetime_prompt_validator)
        date_time_prompt.telemetry_client = telemetry_client
        self.add_dialog(date_time_prompt)
        waterfall_dialog = WaterfallDialog(WaterfallDialog.__name__ + "2", [self.initial_step, self.final_step])
        waterfall_dialog.telemetry_client = telemetry_client       
        self.add_dialog(waterfall_dialog)
        self.initial_dialog_id = WaterfallDialog.__name__ + "2"

    
    async def initial_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        timex = step_context.options
        msg = "When would you like return ?"
        prompt_msg = MessageFactory.text(msg, msg, InputHints.expecting_input)
        msg_text = (
            "I'm sorry, for best results, please enter your travel "
            "date including the day, month and year, e.g. 10 January 2022")
        reprompt_msg = MessageFactory.text(msg_text, msg_text, InputHints.expecting_input)
        if timex is None:
            return await step_context.prompt(
                DateTimePrompt.__name__,
                PromptOptions(prompt=prompt_msg, retry_prompt=reprompt_msg))
        if "definite" in Timex(timex).types:
            return await step_context.prompt(DateTimePrompt.__name__, PromptOptions(prompt=reprompt_msg))
        return await step_context.next(DateTimeResolution(timex=timex))

    
    async def final_step(self, step_context: WaterfallStepContext):       
        timex = step_context.result[0].timex
        return await step_context.end_dialog(timex)

    
    @staticmethod
    async def datetime_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if prompt_context.recognized.succeeded:
            timex = prompt_context.recognized.value[0].timex.split("T")[0]
            return "definite" in Timex(timex).types
        return False
