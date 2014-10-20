from superdesk.tests import TestCase
from apps.preferences import PreferencesService

class Preference_Tests(TestCase):

    _default_user_settings =  {
        "archive:view": {
            "default": "mgrid",
            "label": "Users archive view format",
            "type": "string",
            "category": "archive",
            "allowed": [
                "mgrid",
                "compact"
            ],
            "view": "mgrid"
        },
        "feature:preview": {
            "category": "feature",
            "default": 'false',
            "type": "bool",
            "enabled": 'false',
            "label": "Andrew"
        },
        "email:notification": {
            "category": "notifications",
            "default": 'true',
            "type": "bool",
            "enabled": 'true',
            "label": "Send Hello"
        }
    }

    _default_session_settings =  {
        "desk:items": [],
        "pinned:items": [],
        "scratchpad:items": []
    }


    _session_update = {
        "session_preferences": {
            "scratchpad:items": [123]
        }
    }

    _user_update = { "user_preferences": {
            "archive:view": {
                "label": "Testing user preferences"
            }
        }
    }


    def test_setting_partial_session_preferences_with_empty_existing(self):
        update = self._session_update
        PreferencesService.partial_update(self, update, {}, self._default_session_settings, "session_preferences")
        self.assertListEqual(update["session_preferences"]["scratchpad:items"], [123])

    def test_setting_partial_session_preferences_with_existing(self):
        existing_session_settings =  {
        "desk:items": [],
        "pinned:items": ['a', 'b', 'c'],
        "scratchpad:items": []
        }

        update = self._session_update
        PreferencesService.partial_update(self, update, existing_session_settings, self._default_session_settings, "session_preferences")
        self.assertListEqual(update["session_preferences"]["scratchpad:items"], [123])

    def test_setting_partial_user_preferences_with_existing(self):
        update = self._user_update
        PreferencesService.partial_update(self, update, {}, self._default_user_settings, "user_preferences")
        self.assertEqual(update["user_preferences"]["archive:view"]["label"], "Testing user preferences")

    def test_setting_partial_user_preferences_with_empty_existing(self):
        update = self._user_update
        existing_user_settings =  {
            "archive:view": {
                "default": "mgrid",
                "label": "Users archive view format",
                "type": "string",
                "category": "archive",
                "allowed": [
                    "mgrid",
                    "compact"
                ],
                "view": "mgrid"
            }
        }

        PreferencesService.partial_update(self, update, existing_user_settings, self._default_user_settings, "user_preferences")
        self.assertEqual(update["user_preferences"]["archive:view"]["label"], "Testing user preferences")
