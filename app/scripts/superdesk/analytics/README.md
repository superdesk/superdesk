# Analytics module

This module enables client usage tracking.

Analytics providers:

- piwik
- google analytics

### Piwik setup

Set `PIWIK_URL` and `PIWIK_SITE_ID` environment variables and build client.

    export PIWIK_URL="http://piwik.example.com"
    export PIWIK_SITE_ID="1"
    grunt build

### Google Analytics setup

Set `TRACKING_ID` environment variable to your analytics Tracking ID.

    export TRACKING_ID="UA-123456"
    grunt build
