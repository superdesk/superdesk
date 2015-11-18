
Feature: Content Filter

  @auth
  @vocabulary
  Scenario: Add a new content filter
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "content_filters"
    When we post to "/content_filters" with success
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
    """
    Then we get latest
    When we post to "/content_filters" with success
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"], "pf": ["#content_filters._id#"]}}], "name": "complex"}]
    """
    And we get "/content_filters"
    Then we get list with 2 items
    """
    {
      "_items":
        [
          {"name": "soccer-only"},
          {"name": "complex"}
        ]
    }
    """

  @auth
  @vocabulary
  Scenario: Add a new content filter without global filter value
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "content_filters"
    When we post to "/content_filters" with success
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer"}]
    """
    And we get "/content_filters"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"is_global": false}
        ]
    }
    """

  @auth
  @vocabulary
  Scenario: Add a new content filter with the same name fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "content_filters"
    When we post to "/content_filters" with success
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer"}]
    """
    Then we get latest
    When we post to "/content_filters"
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"], "pf": ["#content_filters._id#"]}}], "name": "soccer"}]
    """
    Then we get error 400
    """
    {"_status": "ERR", "_issues": {"name": {"unique": 1}}}
    """

  @auth
  @vocabulary
  Scenario: Deleting content filter referenced by other content filters fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "content_filters"
    When we post to "/content_filters" with success
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer"}]
    """
    Then we get latest
    When we post to "/content_filters" with success
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"], "pf": ["#content_filters._id#"]}}], "name": "tennis"}]
    """
    When we delete content filter "soccer"
    Then we get error 400
    When we delete content filter "tennis"
    Then we get error 204

  @auth
  @vocabulary
  Scenario: Deleting content filter referenced by subscribers fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """
    Then we get latest

    Given empty "content_filters"
    When we post to "/content_filters" with success
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer"}]
    """
    Then we get latest

    Given empty "subscribers"
    When we post to "/subscribers" with success
    """
    {
        "name": "Subscriber Foo",
        "media_type": "media",
        "subscriber_type": "digital",
        "sequence_num_settings":{"min" : 1, "max" : 10},
        "email": "foo@bar.com",
        "destinations": [{
            "name": "destination1",
            "format": "nitf",
            "delivery_type": "FTP",
            "config": {"ip":"127.0.0.1", "password": "xyz"}
        }],
        "content_filter": {
            "filter_id": "#content_filters._id#",
            "filter_type": "blocking"
        }
    }
    """
    Then we get latest

    When we delete content filter "soccer"
    Then we get error 400

  @auth
  @vocabulary
  Scenario: Deleting content filter referenced by routing schemes fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """
    Then we get latest

    Given empty "content_filters"
    When we post to "/content_filters" with success
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer"}]
    """
    Then we get latest

    Given empty "routing_schemes"
    When we post to "/routing_schemes"
    """
    {
        "name": "routing scheme 1",
        "rules": [{
            "name": "Sports Rule",
            "filter": "#content_filters._id#",
            "actions": {
                "fetch": []
            }
        }]
    }
    """
    Then we get latest

    When we delete content filter "soccer"
    Then we get error 400
