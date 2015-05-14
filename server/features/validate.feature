
Feature: Validate

  @auth
  Scenario: Validate type
    Given the "validators"
      """
      [{"_id": "publish", "schema":{"headline": {"type": "string"}}}]
      """
    When we post to "/validate"
      """
      {"act": "publish", "validate": {"headline": true}}
      """
    Then we get existing resource
    """
    {"errors": ["HEADLINE must be of string type"]}
    """

  @auth
  Scenario: Validate pass
    Given the "validators"
      """
      [{"_id": "publish", "schema":{"headline": {"type": "string"}}}]
      """
    When we post to "/validate"
      """
      {"act": "publish", "validate": {"headline": "budget cigs and beer up"}}
      """
    Then we get existing resource
    """
    {"errors": ""}
    """

  @auth
  Scenario: Validate required field
    Given the "validators"
      """
      [{"_id": "publish", "schema":{"headline": {"type": "string", "required": true}}}]
      """
    When we post to "/validate"
      """
      {"act": "publish", "validate": {"not headline": "budget cigs and beer up"}}
      """
    Then we get existing resource
    """
    {"errors": ["HEADLINE is a required field"]}
    """
  @auth
  Scenario: Validate field length short
    Given the "validators"
      """
      [{"_id": "publish", "schema":{"headline": {"type": "string", "minlength": 2, "maxlength": 55}}}]
      """
    When we post to "/validate"
      """
      {"act": "publish", "validate": {"headline": "1"}}
      """
    Then we get existing resource
    """
    {"errors": ["HEADLINE is too short"]}
    """

  @auth
  Scenario: Validate field length long
    Given the "validators"
      """
      [{"_id": "publish", "schema":{"headline": {"type": "string", "minlength": 2, "maxlength": 3}}}]
      """
    When we post to "/validate"
      """
      {"act": "publish", "validate": {"headline": "1234"}}
      """
    Then we get existing resource
    """
    {"errors": ["HEADLINE is too long"]}
    """

  @auth
  Scenario: Validate allowed values
    Given the "validators"
      """
      [{"_id": "publish", "schema":{"type": {"type": "string", "allowed": ["X","T"]}}}]
      """
    When we post to "/validate"
      """
      {"act": "publish", "validate": {"type": "B"}}
      """
    Then we get existing resource
    """
    {"errors": ["TYPE unallowed value B"]}
    """
  @auth
  Scenario: Validate allow unknown fields
    Given the "validators"
      """
      [{"_id": "publish", "schema":{}}]
      """
    When we post to "/validate"
      """
      {"act": "publish", "validate": {"unknown": "B"}}
      """
    Then we get existing resource
    """
    {"errors": {}}
    """
  @auth
  Scenario: Missing validator
    Given the "validators"
      """
      [{"_id": "publish", "schema":{}}]
      """
    When we post to "/validate"
      """
      {"act": "missing", "validate": {"unknown": "B"}}
      """
    Then we get existing resource
    """
    {"errors": ["validator was not found for missing"]}
    """