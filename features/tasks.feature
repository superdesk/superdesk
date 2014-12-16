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
        [{"slugline": "first task", "type": "text", "task": {"desk":"#DESKS_ID#"}}]
	    """
        When we post to "archive"
        """
        [{"type": "text"}]
        """
        And we get "/tasks"
        Then we get list with 1 items
	    """
        {"_items": [{"slugline": "first task", "type": "text", "task": {"desk": "#DESKS_ID#"}}]}
	    """

    @auth
    Scenario: Update task description
        Given "tasks"
        """
        [{"slugline": "testtask", "task": {"status": "in-progress"}}]
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
        [{"slugline": "testtask", "task": {"status": "in-progress"}}]
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
        {"username": "foo", "email": "foo@bar.com"}
        """
        When we post to "desks"
        """
        {"name": "Sports Desk"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"user": "#USERS_ID#"}}]
	    """
        And we patch latest
        """
        {"description_text": "second task modified", "task": {"desk":"#DESKS_ID#"}}
        """
        Then we get updated response

    @auth
    Scenario: Existing archive item - update task-user asignment
        Given empty "desks"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com"}
        """
        When we post to "desks"
        """
        {"name": "Sports Desk"}
        """
        When we post to "archive"
	    """
        [{"headline": "test"}]
	    """
        When we patch "/tasks/#ARCHIVE_ID#"
	    """
        {"slugline": "first task", "type": "text", "task": {"user": "#USERS_ID#"}}
	    """
        Then we get updated response

    @auth
    Scenario: Fill stage automatically when assigning a task to a desk
        Given empty "desks"
        Given empty "tasks"
        When we post to "desks"
        """
        {"name": "Sports Desk"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"desk": "#DESKS_ID#"}}]
	    """
        Then we get stage filled in to default_incoming


    @auth
    Scenario: Update task-planning item assignment
        Given empty "planning"
        Given empty "tasks"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com"}
        """
        When we post to "planning"
        """
        {"slugline": "test planning item"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"user": "#USERS_ID#"}}]
	    """
        And we patch latest
        """
        {"description_text": "second task modified", "planning_item":"#PLANNING_ID#"}
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
        [{"name": "Test Stage", "desk": "#DESKS_ID#", "task_status": "done"}]
        """
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"user": "#USERS_ID#"}}]
	    """
        Then we get existing resource
        """
        {"task": {"status": "todo"}}
        """
        When we patch latest
        """
        {"task": {"user": "#USERS_ID#", "desk": "#DESKS_ID#", "stage": "#STAGES_ID#"}}
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
        {"username": "foo", "email": "foo@bar.com"}
        """
        When we post to "tasks"
	    """
        [{"slugline": "first task", "type": "text", "task": {"user": "#USERS_ID#"}}]
	    """
        And we delete latest
        Then we get deleted response
