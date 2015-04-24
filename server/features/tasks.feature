Feature: Tasks

    @auth
    Scenario: List empty tasks
        Given empty "tasks"
        When we get "/tasks"
        Then we get list with 0 items

    @auth
    Scenario: Create new task
        Given empty "desks"
        Given empty "archive"
        Given empty "tasks"
        When we post to "desks"
        """
        {"name": "Sports Desk"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"desk":"#desks._id#"}}]
	    """
        When we post to "archive"
        """
        [{"type": "text"}]
        """
        And we get "/tasks"
        Then we get list with 1 items
	    """
        {"_items": [{"slugline": "first task", "type": "text", "task": {"desk": "#desks._id#"}}]}
	    """

    @auth
    Scenario: Update task description
        Given "tasks"
        """
        [{"slugline": "testtask", "task": {"status": "in_progress"}}]
        """
        When we patch given
        """
        {"slugline": "testtask changed"}
        """
        And we get "/tasks"
        Then we get list with 1 items
	    """
        {"_items": [{"slugline": "testtask changed"}]}
	    """

    @auth
    Scenario: Update multiple task description
        Given "tasks"
        """
        [{"slugline": "testtask", "task": {"status": "in_progress"}}]
        """
        When we patch given
        """
        {"description_text":"the test task modified"}
        """
        And we patch latest
        """
        {"description_text":"the test of the test task modified"}
        """
        Then we get updated response

    @auth
    Scenario: Update task-desk asignment
        Given empty "desks"
        Given empty "tasks"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com", "sign_off": "abc"}
        """
        When we post to "desks"
        """
        {"name": "Sports Desk"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"user": "#users._id#"}}]
	    """
        And we patch latest
        """
        {"description_text": "second task modified", "task": {"desk":"#desks._id#"}}
        """
        Then we get updated response

    @auth
    Scenario: Update task-planning item assignment
        Given empty "planning"
        Given empty "tasks"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com", "sign_off": "abc"}
        """
        When we post to "planning"
        """
        {"slugline": "test planning item"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"user": "#users._id#"}}]
	    """
        And we patch latest
        """
        {"description_text": "second task modified", "planning_item":"#planning._id#"}
        """
        Then we get updated response


    @auth
    Scenario: Update task status on stage change
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Desk1"}]
        """
        When we post to "stages"
        """
        [{"name": "Test Stage", "desk": "#desks._id#", "task_status": "done"}]
        """
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com", "sign_off": "abc"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"user": "#users._id#"}}]
	    """
        Then we get existing resource
        """
        {"task": {"status": "todo"}}
        """
        When we patch latest
        """
        {"task": {"user": "#users._id#", "desk": "#desks._id#", "stage": "#stages._id#"}}
        """
        Then we get existing resource
        """
        {"task": {"status": "done"}}
        """


    @auth
    Scenario: Delete task
        Given empty "tasks"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com", "sign_off": "abc"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"user": "#users._id#"}}]
	    """
        And we delete latest
        Then we get deleted response
