Feature: Vocabularies

  @auth
  Scenario: List category vocabulary
    Given the "vocabularies"
      """
      [{"_id": "categories", "items": [{"name": "National", "value": "A", "is_active": true}, {"name": "Domestic Sports", "value": "T", "is_active": false}]}]
      """
    When we get "/vocabularies/categories"
    Then we get existing resource
      """
      {"_id": "categories", "items": [{"name": "National", "value": "A"}]}
      """

  @auth
  Scenario: List default preferred categories vocabulary
    Given the "vocabularies"
      """
      [{
          "_id": "default_categories",
          "items": [
              {"is_active": true, "qcode": "a"},
              {"is_active": false, "qcode": "b"},
              {"is_active": true, "qcode": "c"}
          ]
        }
      ]
      """
    When we get "/vocabularies/default_categories"
    Then we get existing resource
      """
      {"_id": "default_categories", "items": [{"qcode": "a"}, {"qcode": "c"}]}
      """

  @auth
  Scenario: List newsvalue vocabulary
    Given the "vocabularies"
      """
      [{"_id": "newsvalue", "items":[{"name":"1","value":"1", "is_active": true},{"name":"2","value":"2","is_active": true},{"name":"3","value":"3", "is_active": true},{"name":"4","value":"4", "is_active": false}]}]
      """
    When we get "/vocabularies/newsvalue"
    Then we get existing resource
      """
      {"_id": "newsvalue", "items":[{"name":"1","value":"1"},{"name":"2","value":"2"},{"name":"3","value":"3"}]}
      """

  @auth
  Scenario: List vocabularies
    Given the "vocabularies"
      """
      [
        {"_id": "categories", "items": [{"name": "National", "value": "A", "is_active": true}, {"name": "Domestic Sports", "value": "T", "is_active": false}]},
        {"_id": "newsvalue", "items":[{"name":"1","value":"1", "is_active": true},{"name":"2","value":"2","is_active": true},{"name":"3","value":"3", "is_active": true},{"name":"4","value":"4", "is_active": false}]}
      ]
      """
    When we get "/vocabularies"
    Then we get existing resource
      """
      {
        "_items" :
          [
            {"_id": "categories", "items": [{"name": "National", "value": "A"}]},
            {"_id": "newsvalue", "items":[{"name":"1","value":"1"},{"name":"2","value":"2"},{"name":"3","value":"3"}]}
          ]
      }
      """

  @auth
  Scenario: Fetch active keywords only when requested for vocabularies and fetch both active and inactive keywords when requested for keywords
    Given the "vocabularies"
    """
    [{"_id": "keywords", "items": [{"is_active": true, "name": "Health", "value": "Health"}, {"is_active": false, "name": "Motoring", "value": "Motoring"}]}]
    """
    When we get "/vocabularies"
    Then we get existing resource
    """
    {"_items":[{"_id": "keywords", "items": [{"name": "Health", "value": "Health"}]}]}
    """
    When we get "/vocabulary/keywords"
    Then we get existing resource
    """
    {"_items":[{"is_active": true, "name": "Health", "value": "Health"}, {"is_active": false, "name": "Motoring", "value": "Motoring"}]}
    """
    When we get "/vocabulary/keywords?where={"name": "Health"}"
    Then we get existing resource
    """
    {"_items":[{"is_active": true, "name": "Health", "value": "Health"}]}
    """

  @auth
  Scenario: Creates Keywords Vocabulary
    Given empty "vocabularies"
    When we post to "/vocabulary/keywords"
    """
    [{"name": "Health", "value": "Health"}]
    """
    Then we get OK response
    When we get "/vocabulary/keywords?where={"name": "Health"}"
    Then we get existing resource
    """
    {"_items":[{"is_active": true, "name": "Health", "value": "Health"}]}
    """

  @auth
  Scenario: Adding an inactive Keyword makes it active
    Given the "vocabularies"
    """
    [{"_id": "keywords", "items": [{"is_active": true, "name": "Health", "value": "Health"}, {"is_active": false, "name": "Motoring", "value": "Motoring"}]}]
    """
    When we post to "/vocabulary/keywords"
    """
    [{"name": "Motoring", "value": "Motoring"}]
    """
    Then we get OK response
    When we get "/vocabulary/keywords?where={"name": "Motoring"}"
    Then we get existing resource
    """
    {"_items":[{"is_active": true, "name": "Motoring", "value": "Motoring"}]}
    """

  @auth
  Scenario: Avoids creation of duplicate Keywords
    Given the "vocabularies"
    """
    [{"_id": "keywords", "items": [{"is_active": true, "name": "Health", "value": "Health"}, {"is_active": false, "name": "Motoring", "value": "Motoring"}]}]
    """
    When we post to "/vocabulary/keywords"
    """
    [{"name": "Health", "value": "Health"}]
    """
    Then we get error 400
    """
    {"_message": "Keyword with name Health already exists"}
    """

  @auth
  Scenario: Update a Keyword in the Keywords Vocabulary
    Given the "vocabularies"
    """
    [{"_id": "keywords", "items": [{"is_active": true, "name": "Health", "value": "Health"}, {"is_active": true, "name": "Motor", "value": "Motor"}]}]
    """
    When we patch "/vocabulary/keywords/Motor"
    """
    {"name": "Motoring", "value": "Motoring"}
    """
    And we get "/vocabulary/keywords?where={"name": "Motoring"}"
    Then we get existing resource
    """
    {"_items":[{"is_active": true, "name": "Motoring", "value": "Motoring"}]}
    """

  @auth
  Scenario: Updating an inactive Keyword in the Keywords Vocabulary throws 400
    Given the "vocabularies"
    """
    [{"_id": "keywords", "items": [{"is_active": true, "name": "Health", "value": "Health"}, {"is_active": false, "name": "Motor", "value": "Motor"}]}]
    """
    When we patch "/vocabulary/keywords/Motor"
    """
    {"name": "Motoring", "value": "Motoring"}
    """
    Then we get error 400
    """
    {"_issues": {"validator exception": "404: Keyword with name Motor not found"}}
    """

  @auth
  Scenario: Deleting a Keyword from Vocabulary
    Given the "vocabularies"
    """
    [{"_id": "keywords", "items": [{"is_active": true, "name": "Health", "value": "Health"}, {"is_active": true, "name": "Motor", "value": "Motor"}]}]
    """
    When we delete "/vocabulary/keywords/Motor"
    Then we get deleted response

  @auth
  Scenario: Deleting an inactive Keyword from Vocabulary throws 404
    Given the "vocabularies"
    """
    [{"_id": "keywords", "items": [{"is_active": true, "name": "Health", "value": "Health"}, {"is_active": false, "name": "Motor", "value": "Motor"}]}]
    """
    When we delete "/vocabulary/keywords/Motor"
    Then we get error 404
    """
    {"_message": "Keyword with name Motor not found"}
    """

  @auth
  Scenario: User can't perform POST, PATCH and DELETE operation without sufficient privileges
    Given the "vocabularies"
    """
    [{"_id": "keywords", "items": [{"is_active": true, "name": "Health", "value": "Health"}, {"is_active": true, "name": "Motor", "value": "Motor"}]}]
    """
    When we login as user "foo" with password "bar" and user type "user"
    """
    {"user_type": "user", "email": "foo.bar@foobar.org"}
    """
    And we post to "/vocabulary/keywords"
    """
    [{"name": "Health", "value": "Health"}]
    """
    Then we get response code 403
    When we patch "/vocabulary/keywords/Motor"
    """
    {"name": "Motoring", "value": "Motoring"}
    """
    Then we get response code 403
    When we delete "/vocabulary/keywords/Motor"
    Then we get response code 403
