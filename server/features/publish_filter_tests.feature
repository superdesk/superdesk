Feature: Publish Filter Tests

  @auth
  @vocabulary
  Scenario: Test existing publish filter to get matching articles
    Given empty "archive"
    When we post to "/archive"
    """
    [{"urgency": 1}]
    """
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "urgency", "operator": "in", "value": "1,2,3"}]
    """
    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
    """
    When we post to "/publish_filters/test"
    """
    [{"return_matching": true, "filter_id": "#publish_filters._id#"}]
    """
    Then we get existing resource
    """
    {
      "match_results": [{"urgency": 1}]
    }
    """

  @auth
  @vocabulary
  Scenario: Test in-memory publish filter to get matching articles
    Given empty "archive"
    When we post to "/archive"
    """
    [{"urgency": 1}]
    """
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "urgency", "operator": "in", "value": "1,2,3"}]
    """
    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters/test"
    """
    [{"return_matching": true, "filter": {"publish_filter": [{"expression" : {"fc" : ["#filter_conditions._id#"]}}]}}]
    """
    Then we get existing resource
    """
    {
      "match_results": [{"urgency": 1}]
    }
    """

  @auth
  @vocabulary
  Scenario: Test publish filter to get non-matching articles
    Given empty "archive"
    When we post to "/archive"
    """
    [{"urgency": 1}]
    """
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "urgency", "operator": "in", "value": "2,3"}]
    """
    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
    """
    When we post to "/publish_filters/test"
    """
    [{"return_matching": false, "filter_id": "#publish_filters._id#"}]
    """
    Then we get existing resource
    """
    {
      "match_results": [{"urgency": 1}]
    }
    """

  @auth
  @vocabulary
  Scenario: Test in-memory publish filter to get non-matching articles
    Given empty "archive"
    When we post to "/archive"
    """
    [{"urgency": 5}]
    """
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "urgency", "operator": "in", "value": "1,2,3"}]
    """
    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters/test"
    """
    [{"return_matching": false, "filter": {"publish_filter": [{"expression" : {"fc" : ["#filter_conditions._id#"]}}]}}]
    """
    Then we get existing resource
    """
    {
      "match_results": [{"urgency": 5}]
    }
    """

  @auth
  @vocabulary
  Scenario: Test a single article
    Given empty "archive"
    When we post to "/archive"
    """
    [{"urgency": 1}]
    """
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "urgency", "operator": "in", "value": "1,2,3"}]
    """
    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
    """
    When we post to "/publish_filters/test"
    """
    [{"filter_id": "#publish_filters._id#", "article_id":"#archive._id#"}]
    """
    Then we get existing resource
    """
    {
      "match_results": true
    }
    """

  @auth
  @vocabulary
  Scenario: Test in-memory publish filter to single article
    Given empty "archive"
    When we post to "/archive"
    """
    [{"urgency": 5}]
    """
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "urgency", "operator": "in", "value": "1,2,3"}]
    """
    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters/test"
    """
    [{"filter": {"publish_filter": [{"expression" : {"fc" : ["#filter_conditions._id#"]}}]},
      "article_id": "#archive._id#"}]
    """
    Then we get existing resource
    """
    {
      "match_results": false
    }
    """
