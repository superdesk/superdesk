Feature: Packages

    @auth
    Scenario: Create new package without groups
        Given empty "archive"
        When we post to "archive"
        """
        {"groups": [], "guid": "tag:example.com,0000:newsml_BRE9A605", "type": "composite"}
        """
        Then we get error 400
        """
        {
            "_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"},
            "_issues": {"groups": {"minlength": 1}},
            "_status": "ERR"
        }
        """

    @auth
    Scenario: Create new package without desk
        Given empty "archive"
        When we post to "archive"
        """
        {"guid": "tag:example.com,0000:newsml_BRE9A605", "type": "composite", "task": {}}
        """
        Then we get error 403
        """
        {
            "_message": "Packages can not be created in the personal space.",
            "_status": "ERR"
        }
        """

    @auth
    Scenario: Create new package with text content
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive" with success
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A606"}]
        """
        When we post to "archive" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "type": "composite",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        And we get "archive?source={"query":{"filtered":{"filter":{"and":[{"terms":{"type":["composite"]}}]}}}}"
        Then we get list with 1 items
        """
        {
            "_items": [
                {
                    "groups": [
                        {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                        {
                            "id": "main",
                            "refs": [
                                {
                                    "headline": "test package with text",
                                    "residRef": "tag:example.com,0000:newsml_BRE9A606",
                                    "slugline": "awesome article"
                                }
                            ],
                            "role": "grpRole:Main"
                        }
                    ],
                    "guid": "tag:example.com,0000:newsml_BRE9A605"
                }
            ]
        }
        """

    @auth
    Scenario: Create new package with image content
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When upload a file "bike.jpg" to "archive" with "tag:example.com,0000:newsml_BRE9A605"
        When we post to "archive" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with pic",
                            "residRef": "tag:example.com,0000:newsml_BRE9A605",
                            "slugline": "awesome picture"
                        }
                    ],
                    "role": "main"
                }
            ],
            "type": "composite",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        And we get "archive?source={"query":{"filtered":{"filter":{"and":[{"not":{"term":{"state":"spiked"}}},{"terms":{"type":["composite"]}}]}}}}"
        Then we get list with 1 items
        """
        {
            "_items": [
                {
                    "groups": [
                        {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                        {
                            "id": "main",
                            "refs": [
                                {
                                    "headline": "test package with pic",
                                    "residRef": "tag:example.com,0000:newsml_BRE9A605",
                                    "slugline": "awesome picture"
                                }
                            ],
                            "role": "main"
                        }
                    ]
                }
            ]
        }
        """

    @auth
    Scenario: Create package with image and text
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When upload a file "bike.jpg" to "archive" with "tag:example.com,0000:newsml_BRE9A605"
        When we post to "archive"
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A606"}]
        """
        When we post to "archive" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with pic",
                            "residRef": "tag:example.com,0000:newsml_BRE9A605",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "type": "composite",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        And we get "archive?source={"query":{"filtered":{"filter":{"and":[{"not":{"term":{"state":"spiked"}}},{"terms":{"type":["composite"]}}]}}}}"
        Then we get list with 1 items
        """
        {
            "_items": [
                {
                    "groups": [
                        {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                        {
                            "id": "main",
                            "refs": [
                                {
                                    "headline": "test package with pic",
                                    "residRef": "tag:example.com,0000:newsml_BRE9A605",
                                    "slugline": "awesome picture"
                                },
                                {
                                    "headline": "test package with text",
                                    "residRef": "tag:example.com,0000:newsml_BRE9A606",
                                    "slugline": "awesome article"
                                }
                            ],
                            "role": "main"
                        }
                    ]
                }
            ]
        }
        """

    @auth
    Scenario: Fail on creating new package with duplicated content
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        {
            "type": "composite",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with pic",
                            "residRef": "#archive._id#",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "#archive._id#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        Then we get error 403
        """
        {"_message": "Content associated multiple times", "_status": "ERR"}
        """

    @auth
    Scenario: Fail on creating package with circular reference
        Given "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A606"}]
        """
        When we post to "archive" with success
        """
        {
            "type": "composite",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        When we post to "archive" with success
        """
        {
            "type": "composite",
            "guid": "tag:example.com,0000:newsml_BRE9A604",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A605",
                            "slugline": "awesome circular article"
                        }
                    ],
                    "role": "main story"
                }
            ],
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        And we patch "/archive/tag:example.com,0000:newsml_BRE9A605"
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A604",
                            "slugline": "awesome circular article"
                        }
                    ]
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
        }
        """
        Then we get error 400
        """
        {
            "_issues": {"validator exception": "Trying to create a circular reference to: tag:example.com,0000:newsml_BRE9A604"},
            "_status": "ERR"
        }
        """

    @auth
    Scenario: Retrieve created package
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A606"}]
        """
        When we post to "archive" with success
        """
        {
            "type": "composite",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        Then we get new resource
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "type": "composite"
        }
        """
        And we get latest
        When we get "archive"
        Then we get list with 2 items
        """
        {
            "_items": [
                {
                    "guid": "tag:example.com,0000:newsml_BRE9A606",
                    "headline": "test",
                    "linked_in_packages": [{"package": "tag:example.com,0000:newsml_BRE9A605"}],
                    "type": "text"
                },
                {
                    "groups": [
                        {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                        {
                            "id": "main",
                            "refs": [
                                {
                                    "headline": "test package with text",
                                    "residRef": "tag:example.com,0000:newsml_BRE9A606",
                                    "slugline": "awesome article"
                                }
                            ],
                            "role": "main"
                        }
                    ],
                    "guid": "tag:example.com,0000:newsml_BRE9A605",
                    "type": "composite"
                }
            ]
        }
        """

    @auth
    Scenario: Fail on creating new package with missing root group
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "archive"
        """
        {
            "type": "composite",
            "groups": [
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#archive._id#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        Then we get error 403
        """
        {"_message": "Root group is missing.", "_status": "ERR"}
        """

    @auth
    Scenario: Fail on creating new package with duplicated root group
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "archive"
        """
        {
            "type": "composite",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#archive._id#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        Then we get error 403
        """
        {"_message": "Only one root group is allowed.", "_status": "ERR"}
        """

    @auth
    Scenario: Fail on creating new package with missing group referenced in root
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "archive"
        """
        {
            "type": "composite",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}, {"idRef": "sidebar"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#archive._id#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        Then we get error 403
        """
        {"_message": "The number of groups and of referenced groups in the root group do not match.", "_status": "ERR"}
        """

    @auth
    Scenario: Fail on creating new package with group not referenced in root
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "archive"
        """
        {
            "type": "composite",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}, {"idRef": "sidebar"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#archive._id#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                },
                {
                    "id": "story",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#archive._id#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Story"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        Then we get error 403
        """
        {"_message": "Not all groups are referenced in the root group.", "_status": "ERR"}
        """

    @auth
    Scenario: Fail on patching created package with group not referenced in root
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A606"}]
        """
        When we upload a file "bike.jpg" to "archive"
        When we post to "archive" with success
        """
        {
            "type": "composite",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "residRef": "#archive._id#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        And we patch latest without assert
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with pic",
                            "residRef": "#archive._id#",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                },
                {
                    "id": "story",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "story"
                }
            ]
        }
        """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": {"validator exception": "403: The number of groups and of referenced groups in the root group do not match."}}
        """

    @auth
    Scenario: Patch created package
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A606"}]
        """
        When upload a file "bike.jpg" to "archive" with "tag:example.com,0000:newsml_BRE9A604"
        When we post to "archive" with success
        """
        {
            "type": "composite",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        And we patch latest
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with pic",
                            "residRef": "tag:example.com,0000:newsml_BRE9A604",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ]
        }
        """
        Then we get existing resource
        """
        {
            "_id": "tag:example.com,0000:newsml_BRE9A605",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with pic",
                            "residRef": "tag:example.com,0000:newsml_BRE9A604",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "type": "composite"
        }
        """
        And we get version 2
       	When we get "/archive/tag:example.com,0000:newsml_BRE9A605?version=all"
        Then we get list with 2 items

    @auth
    Scenario: When removing a link from the package, item.linked_in_packages gets updated
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"guid": "tag:example.com,0000:newsml_BRE9A679", "headline": "test"}]
        """
        And we save etag
        When we post to "archive" with success
        """
        {
            "type": "composite",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A679",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        And we patch latest
        """
        {"groups": [{"id": "root", "refs": [], "role": "grpRole:NEP"}]}
        """
        Then we get existing resource
        """
        {
            "_id": "tag:example.com,0000:newsml_BRE9A605",
            "groups": [{"id": "root", "refs": [], "role": "grpRole:NEP"}],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "type": "composite"
        }
        """
        And we get version 2
        When we get "/archive/tag:example.com,0000:newsml_BRE9A679"
        Then we get existing resource
        """
        {"headline": "test", "linked_in_packages": []}
        """
        And we get same etag


    @auth
    Scenario: Delete created package
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive"
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A679"}]
        """
        When we post to "archive" with success
        """
        {
            "type": "composite",
            "guid": "tag:example.com,0000:newsml_BRE9A678",
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A679",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        When we delete "/archive/tag:example.com,0000:newsml_BRE9A678"
        Then we get response code 405
        When we get "archive"
        Then we get list with 2 items
        """
        {"_items": [{"guid": "tag:example.com,0000:newsml_BRE9A679", "headline": "test", "linked_in_packages": [], "type": "text"}]}
        """

    @auth
    Scenario: Can not spike an item in a package
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive" with success
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A606", "slugline": "WORMS"}]
        """
        When we post to "archive" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "type": "composite",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        When we spike "tag:example.com,0000:newsml_BRE9A606"
        Then we get error 400
        """
        {"_issues": {"validator exception": "400: The item \"WORMS\" is in a package it needs to be removed before the item can be spiked"}, "_status": "ERR"}
        """

    @auth
    Scenario: Creating a package with Public Service Announcements fails
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive" with success
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A606"}]
        """
        And we post to "archive"
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "type": "composite",
            "body_footer": "Suicide Call Back Service 1300 659 467",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        Then we get error 400
        """
        {"_message": "Package doesn't support Public Service Announcements"}
        """

    @auth
    Scenario: Updating a package with Public Service Announcements fails
        Given empty "archive"
        And "desks"
        """
        [{"name": "test desk"}]
        """
        When we post to "archive" with success
        """
        [{"headline": "test", "guid": "tag:example.com,0000:newsml_BRE9A606"}]
        """
        And we post to "archive" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "tag:example.com,0000:newsml_BRE9A606",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605",
            "type": "composite",
            "task": {"user": "#user._id#", "desk": "#desks._id#"}
        }
        """
        And we patch "/archive/#archive._id#"
        """
        {"body_footer": "Suicide Call Back Service 1300 659 467"}
        """
        Then we get error 400
        """
        {"_issues": {"validator exception": "400: Package doesn't support Public Service Announcements"}}
        """
