Feature: Packages

    @auth
    Scenario: Empty packages list
        Given empty "packages"
        When we get "/packages"
        Then we get list with 0 items

    @auth
    Scenario: Create new package without groups
        Given empty "packages"
        When we post to "/packages"
        """
        {"groups": [], "guid": "tag:example.com,0000:newsml_BRE9A605"}
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
    Scenario: Create new package with text content
        Given empty "packages"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "/packages" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
        }
        """
        And we get "/packages"
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
                                    "residRef": "#ARCHIVE_ID#",
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
        Given empty "packages"
        When we upload a file "bike.jpg" to "archive_media"
        When we post to "/packages" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with pic",
                            "residRef": "#ARCHIVE_MEDIA_ID#",
                            "slugline": "awesome picture"
                        }
                    ],
                    "role": "main"
                }
            ]
        }
        """
        And we get "/packages"
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
                                    "residRef": "#ARCHIVE_MEDIA_ID#",
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
        Given empty "packages"
        When we upload a file "bike.jpg" to "archive_media"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "/packages" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with pic",
                            "residRef": "#ARCHIVE_MEDIA_ID#",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ]
        }
        """
        And we get "/packages"
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
                                    "residRef": "#ARCHIVE_MEDIA_ID#",
                                    "slugline": "awesome picture"
                                },
                                {
                                    "headline": "test package with text",
                                    "residRef": "#ARCHIVE_ID#",
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
        Given empty "packages"
        When we post to "/packages"
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with pic",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ]
        }
        """
        Then we get error 403
        """
        {"_message": "Content associated multiple times", "_status": "ERR"}
        """

    @auth
    Scenario: Fail on creating package with circular reference
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "/packages" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
        }
        """
        When we post to "/packages" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
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
            ]
        }
        """
        And we patch "/packages/tag:example.com,0000:newsml_BRE9A605"
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "#PACKAGES_ID#",
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
            "_issues": {"validator exception": "Trying to create a circular reference to: #PACKAGES_ID#"},
            "_status": "ERR"
        }
        """

    @auth
    Scenario: Retrieve created package
        Given empty "packages"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "/packages" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
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
                            "residRef": "#ARCHIVE_ID#",
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
        When we get "/archive"
        Then we get list with 2 items
        """
        {
            "_items": [
                {
                    "guid": "#ARCHIVE_ID#",
                    "headline": "test",
                    "linked_in_packages": [{"package": "#PACKAGES_ID#"}],
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
                                    "residRef": "#ARCHIVE_ID#",
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
        Given empty "packages"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "/packages"
        """
        {
            "groups": [
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
        }
        """
        Then we get error 400
        """
        {"_message": "Root group is missing.", "_status": "ERR"}
        """

    @auth
    Scenario: Fail on creating new package with duplicated root group
        Given empty "packages"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "/packages"
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
        }
        """
        Then we get error 400
        """
        {"_message": "Only one root group is allowed.", "_status": "ERR"}
        """

    @auth
    Scenario: Fail on creating new package with missing group referenced in root
        Given empty "packages"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "/packages"
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}, {"idRef": "sidebar"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
        }
        """
        Then we get error 400
        """
        {"_message": "The number of groups and of referenced groups in the root group do not match.", "_status": "ERR"}
        """

    @auth
    Scenario: Fail on creating new package with group not referenced in root
        Given empty "packages"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "/packages"
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}, {"idRef": "sidebar"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
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
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "grpRole:Story"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
        }
        """
        Then we get error 400
        """
        {"_message": "Not all groups are referenced in the root group.", "_status": "ERR"}
        """
    @auth
    Scenario: Fail on patching created package with group not referenced in root
        Given empty "packages"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we upload a file "bike.jpg" to "archive_media"
        When we post to "/packages" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
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
                            "residRef": "#ARCHIVE_MEDIA_ID#",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
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
                            "residRef": "#ARCHIVE_ID#",
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
        {"_issues": {"validator exception": "The number of groups and of referenced groups in the root group do not match."}, "_status": "ERR"}
        """

    @auth
    Scenario: Patch created package
        Given empty "packages"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we upload a file "bike.jpg" to "archive_media"
        When we post to "/packages" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ],
            "guid": "tag:example.com,0000:newsml_BRE9A605"
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
                            "residRef": "#ARCHIVE_MEDIA_ID#",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
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
                            "residRef": "#ARCHIVE_MEDIA_ID#",
                            "slugline": "awesome picture"
                        },
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
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
       	When we get "/packages/tag:example.com,0000:newsml_BRE9A605?version=all"
        Then we get list with 2 items


    @auth
    Scenario: Delete created package
        Given empty "packages"
        When we post to "archive"
        """
        [{"headline": "test"}]
        """
        When we post to "/packages" with success
        """
        {
            "groups": [
                {"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                {
                    "id": "main",
                    "refs": [
                        {
                            "headline": "test package with text",
                            "residRef": "#ARCHIVE_ID#",
                            "slugline": "awesome article"
                        }
                    ],
                    "role": "main"
                }
            ]
        }
        """
        When we delete latest
        Then we get response code 405
        When we get "/archive"
        Then we get list with 2 items
        """
        {"_items": [{"guid": "#ARCHIVE_ID#", "headline": "test", "linked_in_packages": [], "type": "text"}]}
        """
