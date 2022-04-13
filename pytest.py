from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
import os

class DefaultConfig:
    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "") 
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "") 
    LUIS_APP_ID = os.environ.get("LuisAppId", "13bb97b8-0f1d-4df2-a0de-5341f08499b6")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "949f5e56e84c4369aa2564a6a6879b4a")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "https://bookingassistantbot.cognitiveservices.azure.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "3d6e168e-3573-45ba-81e3-b5645b524086"
    )


class test_unit():

    def setUp(self):
        configuration = DefaultConfig()
        client = LUISRuntimeClient('https://' + configuration.LUIS_API_HOST_NAME,CognitiveServicesCredentials(configuration.LUIS_API_KEY))
        request ='I  want to travel from Quimper to Brest from may 10 and return on november 10 2023 with a budget of 10000 euros.'
        self.response = client.prediction.resolve(configuration.LUIS_APP_ID, query=request)
 

    def test_intent(self):
        """Test if the found intent is the right one."""
        self.assertEqual(self.response.top_scoring_intent.intent,'BookFlight')

    def test_origin(self):
        """Test if the found departure city is the right one."""
        for idx, entity in enumerate(self.response.entities):
            if (entity.type == 'or_city') & (entity.entity == "Quimper"):
                self.assertTrue(True)
                return
        self.assertTrue(False)

    def test_destination(self):
        """Test if the found destination city is the right one."""
        for idx, entity in enumerate(self.response.entities):
            if (entity.type == 'dst_city') & (entity.entity == "Brest"):
                self.assertTrue(True)
                return
        self.assertTrue(False)