Feature: Link content in takes

    @auth
    Scenario: Send Content and continue from personal space
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "archive"
        """
        [{
            "guid": "123",
            "type": "text",
            "headline": "test1",
            "slugline": "comics",
            "anpa_take_key": "Take",
            "guid": "123",
            "state": "draft",
            "task": {
                "user": "#CONTEXT_USER_ID#"
            }
        }]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get OK response
        When we post to "archive/123/link"
        """
        [{}]
        """
        Then we get next take
        """
        {
            "type": "text",
            "headline": "test1",
            "slugline": "comics",
            "anpa_take_key": "Take",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#"
        }
        """
        When we get "archive"
        Then we get list with 3 items
        """
        {
            "_items": [
                {
                    "groups": [
                        {"id": "root", "refs": [{"idRef": "main"}]},
                        {
                            "id": "main",
                            "refs": [
                                {
                                    "headline": "test1",
                                    "slugline": "comics",
                                    "residRef": "123",
                                    "sequence": 1
                                },
                                {
                                    "headline": "test1",
                                    "slugline": "comics",
                                    "sequence": 2
                                }
                            ]
                        }
                    ],
                    "type": "composite",
                    "package_type": "takes"
                },
                {
                    "headline": "test1",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}]
                },
                {
                    "guid": "123",
                    "headline": "test1",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}]
                }
            ]
        }
        """
        When we post to "archive/#TAKE#/link"
        """
        [{}]
        """
        Then we get next take
        """
        {
            "type": "text",
            "headline": "test1",
            "slugline": "comics",
            "anpa_take_key": "Take",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#"
        }
        """
        When we get "archive"
        Then we get list with 4 items
        """
        {
            "_items": [
                {
                    "groups": [
                        {"id": "root", "refs": [{"idRef": "main"}]},
                        {
                            "id": "main",
                            "refs": [
                                {
                                    "headline": "test1",
                                    "slugline": "comics",
                                    "residRef": "123",
                                    "sequence": 1
                                },
                                {
                                    "headline": "test1",
                                    "slugline": "comics",
                                    "sequence": 2
                                }
                            ]
                        }
                    ],
                    "type": "composite",
                    "package_type": "takes"
                },
                {
                    "headline": "test1",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}]
                },
                {
                    "guid": "123",
                    "headline": "test1",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}]
                },
                {
                    "guid": "#TAKE#",
                    "headline": "test1",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}]
                }
            ]
        }
        """
