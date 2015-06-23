Feature: Stages

    @auth
    @notification
    Scenario: Add stage and verify order
        Given empty "stages"
        Given "desks"
        """
        [{"name": "test_desk"}]
        """

        When we get "/stages/#desks.incoming_stage#"
        Then we get existing resource
        """
        {
        "name": "New",
        "task_status": "todo",
        "desk": "#desks._id#",
        "desk_order": 1
        }
        """


        When we post to "/stages"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "task_status": "in_progress",
        "desk": "#desks._id#"
        }
        """

        Then we get notifications
        """
        [{"event": "stage", "extra": {"created": 1, "desk_id": "#desks._id#", "stage_id": "#stages._id#", "is_visible": true}}]
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "task_status": "in_progress",
        "desk": "#desks._id#",
        "desk_order": 2
        }
        """

    @auth
    Scenario: Stage name must be unique.
        Given empty "stages"
        Given "desks"
        """
        [{"name": "test_desk"}]
        """

        When we get "/stages/#desks.incoming_stage#"
        Then we get existing resource
        """
        {
        "name": "New",
        "task_status": "todo",
        "desk": "#desks._id#",
        "desk_order": 1
        }
        """
        When we post to "/stages"
        """
        {
        "name": "new",
        "description": "Show content items created by the current logged user",
        "task_status": "in_progress",
        "desk": "#desks._id#"
        }
        """
        Then we get response code 400
        When we post to "/stages"
        """
        {
        "name": "newer",
        "description": "Show content items created by the current logged user",
        "task_status": "in_progress",
        "desk": "#desks._id#"
        }
        """
        Then we get OK response
        When we patch "/stages/#stages._id#"
        """
        {
        "name": "new"
        }
        """
        Then we get response code 400

    @auth
    Scenario: Add stage - no name
        Given empty "stages"
        Given "desks"
        """
        [{"name": "test_desk"}]
        """

        When we post to "/stages"
        """
        {
        "description": "Show content items created by the current logged user"
        }
        """

        Then we get error 400
        """
        {
        "_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"},
        "_issues": {"name": {"required": 1}, "task_status": {"required": 1}, "desk": {"required": 1}}, "_status": "ERR"
        }
        """


    @auth
    Scenario: Add stage - no description
        Given empty "stages"
        Given "desks"
        """
        [{"name": "test_desk"}]
        """

        When we post to "/stages"
        """
        {
        "name": "show my content",
        "task_status": "todo",
        "desk": "#desks._id#"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "task_status": "todo",
        "desk": "#desks._id#",
        "desk_order": 2
        }
        """
        When we patch "/stages/#stages._id#"
        """
        {
        "name": "show my content",
        "task_status": "in_progress",
        "desk": "#desks._id#"
        }
        """
        Then we get latest
        """
        {
        "name": "show my content",
        "task_status": "in_progress",
        "desk": "#desks._id#"
        }
        """

    @auth
    Scenario: Edit stage - modify description and name
        Given empty "stages"
        Given "desks"
        """
        [{"name": "test_desk"}]
        """

        When we post to "/stages"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "task_status": "todo",
        "desk": "#desks._id#"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "task_status": "todo",
        "desk": "#desks._id#"
        }
        """

        When we patch latest
        """
        {
        "description": "Show content that I just updated",
        "name": "My stage"
        }
        """

        Then we get updated response


    @auth @notification
    Scenario: Edit stage - modify expiry
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """

        When we post to "/stages"
        """
        {
        "name": "update expiry",
        "task_status": "todo",
        "desk": "#desks._id#",
        "content_expiry": 10
        }
        """

        Given "archive"
            """
            [{"_id": "testid1", "guid": "testid1", "task": {"desk": "#desks._id#", "stage" :"#stages._id#"}}]
            """

        When we get "archive/testid1"
        Then we get content expiry 10

        When we patch "/stages/#stages._id#"
        """
        {"content_expiry":20 }
        """

        When we get "archive/testid1"
        Then we get content expiry 20
        Then we get notifications
        """
        [{"event": "stage", "extra": {"updated": 1, "desk_id": "#desks._id#", "stage_id": "#stages._id#"}}]
        """

    @auth @notification
    Scenario: Edit stage - set 0 expiry
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """

        When we post to "/stages"
        """
        {
        "name": "update expiry",
        "task_status": "todo",
        "desk": "#desks._id#",
        "content_expiry": 0
        }
        """

        Given "archive"
            """
            [{"_id": "testid1", "guid": "testid1", "task": {"desk": "#desks._id#", "stage" :"#stages._id#"}}]
            """

        When we get "archive/testid1"
        Then we get global content expiry

        When we patch "/stages/#stages._id#"
        """
        {"content_expiry":20 }
        """

        When we get "archive/testid1"
        Then we get content expiry 20
        Then we get notifications
        """
        [{"event": "stage", "extra": {"created": 1, "desk_id": "#desks._id#", "stage_id": "#stages._id#", "is_visible": true}}]
        """

    @auth
    Scenario: Get tasks for stage
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """

        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"desk":"#desks._id#", "stage" :"#desks.incoming_stage#"}}]
	    """
        When we post to "archive"
        """
        [{"type": "text"}]
        """
        And we get "/tasks"

        Then we get list with 1 items
	    """
        {"_items": [{"slugline": "first task", "type": "text", "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]}
	    """

        When we get "/tasks?where={"task.stage": "#desks.incoming_stage#"}"

        Then we get list with 1 items
	    """
        {"_items": [{"slugline": "first task", "type": "text", "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]}
	    """


    @auth
    @notification
    Scenario: Can delete empty stage
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """

        When we post to "/stages"
        """
        {
        "name": "show my content",
        "task_status": "todo",
        "desk": "#desks._id#"
        }
        """

        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"desk":"#desks._id#", "stage" :"#desks.incoming_stage#"}}]
	    """
	    Then we get new resource
        When we post to "archive"
        """
        [{"type": "text"}]
        """
        When we delete "/stages/#stages._id#"
        Then we get response code 204
        Then we get notifications
        """
        [{"event": "stage", "extra": {"deleted": 1}}]
        """


    @auth
    Scenario: Cannot delete stage if there are documents
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """

        When we post to "/stages"
        """
        {
        "name": "show my content",
        "task_status": "todo",
        "desk": "#desks._id#"
        }
        """

        When we patch "/stages/#stages._id#"
        """
        {"desk":"#desks._id#"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"desk":"#desks._id#", "stage" :"#stages._id#"}}]
	    """
	    Then we get new resource
        When we post to "archive"
        """
        [{"type": "text"}]
        """
        When we delete "/stages/#stages._id#"

        Then we get response code 403

    @auth
    @notification
    Scenario: Toggle stage invisibility for notification
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """
        When we post to "/stages"
        """
        {
        "name": "stage visibility",
        "task_status": "todo",
        "desk": "#desks._id#",
        "is_visible" : true
        }
        """
        When we reset notifications
        When we patch "/stages/#stages._id#"
        """
        {"is_visible" : false}
        """
        Then we get response code 200
        Then we get notifications
        """
        [{"event": "stage_visibility_updated", "extra": {"updated": 1, "desk_id": "#desks._id#", "stage_id": "#stages._id#", "is_visible": false}}]
        """


    @auth
    Scenario: Get invisible stages
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """

        When we post to "/stages"
        """
        {
        "name": "invisible1",
        "task_status": "todo",
        "desk": "#desks._id#",
        "is_visible" : false
        }
        """

        When we post to "/stages"
        """
        {
        "name": "invisible2",
        "task_status": "todo",
        "desk": "#desks._id#",
        "is_visible" : false
        }
        """


        Then we get 2 invisible stages


    @auth
    Scenario: Get visible stages
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """

        When we post to "/stages"
        """
        {
        "name": "invisible1",
        "task_status": "todo",
        "desk": "#desks._id#",
        "is_visible" : false
        }
        """

        When we post to "/stages"
        """
        {
        "name": "invisible2",
        "task_status": "todo",
        "desk": "#desks._id#",
        "is_visible" : true
        }
        """


        Then we get 2 visible stages
