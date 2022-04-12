#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os

class DefaultConfig:
    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "d06509e1-2781-4c4a-94d0-ba0b7c990768") 
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "eV+Nc=d9q2Q=]Fcf|oi(sO--") 
    LUIS_APP_ID = os.environ.get("LuisAppId", "13bb97b8-0f1d-4df2-a0de-5341f08499b6")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "949f5e56e84c4369aa2564a6a6879b4a")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "https://bookingassistantbot.cognitiveservices.azure.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "3d6e168e-3573-45ba-81e3-b5645b524086"
    )
