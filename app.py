# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# python3.8 -m aiohttp.web -H 0.0.0.0 -P 8000 app:init_func
from http import HTTPStatus
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (BotFrameworkAdapterSettings, ConversationState, MemoryStorage, UserState)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity
from botbuilder.applicationinsights import ApplicationInsightsTelemetryClient
from botbuilder.integration.applicationinsights.aiohttp import (AiohttpTelemetryProcessor,bot_telemetry_middleware)
from config import DefaultConfig
from dialogs import MainDialog, BookingDialog
from bots import DialogAndWelcomeBot
from adapter_with_error_handler import AdapterWithErrorHandler
from flight_booking_recognizer import FlightBookingRecognizer

CONFIG = DefaultConfig()
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)
ADAPTER = AdapterWithErrorHandler(SETTINGS, CONVERSATION_STATE)
INSTRUMENTATION_KEY = CONFIG.APPINSIGHTS_INSTRUMENTATION_KEY
TELEMETRY_CLIENT = ApplicationInsightsTelemetryClient(INSTRUMENTATION_KEY, telemetry_processor=AiohttpTelemetryProcessor(), client_queue_size=10)
RECOGNIZER = FlightBookingRecognizer(CONFIG)
BOOKING_DIALOG = BookingDialog()
DIALOG = MainDialog(RECOGNIZER, BOOKING_DIALOG, telemetry_client=TELEMETRY_CLIENT)
BOT = DialogAndWelcomeBot(CONVERSATION_STATE, USER_STATE, DIALOG, TELEMETRY_CLIENT)


async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)


def init_func(argv):
    app = web.Application(middlewares=[bot_telemetry_middleware, aiohttp_error_middleware])
    app.router.add_post("/api/messages", messages)
    return app

if __name__ == "__main__":
    app = init_func(None)
    try:
        # Run app in production
        web.run_app(app, host='0.0.0.0', port=CONFIG.PORT)
    except Exception as error:
        raise error
