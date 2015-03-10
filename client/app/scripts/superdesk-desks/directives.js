/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

define([
    'require',
    'lodash',
    'angular'
], function(require, _, angular) {
    'use strict';

    var limits = {
        stage: 15,
        desk: 40
    };

    var app = angular.module('superdesk.desks.directives', []);
    app
    .directive('sdFocusElement', [function() {
        return {
            link: function(scope, elem, attrs) {
                elem.click(function() {
                    _.defer(function() {
                        angular.element(document.querySelector(attrs.target)).focus();
                    });
                });
            }
        };
    }])
    .directive('sdContentExpiry', [function() {
        return {
            templateUrl: 'scripts/superdesk-desks/views/content-expiry.html',
            scope: {
              item: '=',
              preview: '='
            },
            link: function(scope, elem, attrs) {

                var expiryfield = attrs.expiryfield;
                scope.ContentExpiry = {
                    Hours: 0,
                    Minutes: 0,
                    Header: 'Content Expiry'
                };

                scope.$watch('item', function() {
                    setContentExpiry(scope.item);
                });

                scope.$watch('ContentExpiry', function() {
                    if (!scope.item) {
                        scope.item = {};
                    }

                    scope.item[expiryfield] = getTotalExpiryMinutes(scope.ContentExpiry);
                }, true);

                function getExpiryHours(inputMin) {
                    return Math.floor(inputMin / 60);
                }

                function getExpiryMinutes(inputMin) {
                    return Math.floor(inputMin % 60);
                }

                function getTotalExpiryMinutes(contentExpiry) {
                    return (contentExpiry.Hours * 60) + contentExpiry.Minutes;
                }

                var setContentExpiry = function(item) {

                    if (expiryfield !== 'content_expiry') {
                        scope.ContentExpiry.Header = 'Spike Expiry';
                    }

                    if (item && item[expiryfield] != null) {
                        scope.ContentExpiry.Hours = getExpiryHours(item[expiryfield]);
                        scope.ContentExpiry.Minutes = getExpiryMinutes(item[expiryfield]);
                    }
                };
            }
        };
    }])
    .directive('sdDeskeditBasic', ['gettext', 'desks', 'WizardHandler', function(gettext, desks, WizardHandler) {
        return {

            link: function(scope, elem, attrs) {

                scope.limits = limits;

                scope.$watch('step.current', function(step) {
                    if (step === 'general') {
                        if (scope.desk.edit && scope.desk.edit._id) {
                            scope.edit(scope.desk.edit);
                        }
                        scope.message = null;
                    }
                });

                scope.edit = function(desk) {
                    scope.desk.edit = _.create(desk);
                };

                scope.save = function(desk) {
                    scope.message = gettext('Saving...');

                    var _new = desk._id ? false : true;
                    desks.save(scope.desk.edit, desk).then(function() {
                        if (_new) {
                            scope.edit(scope.desk.edit);
                            scope.desks._items.unshift(scope.desk.edit);
                        } else {
                            var origDesk = _.find(scope.desks._items, {_id: scope.desk.edit._id});
                            _.extend(origDesk, scope.desk.edit);
                        }
                        WizardHandler.wizard('desks').next();
                    }, errorMessage);
                };

                function errorMessage(response) {
                    if (response.data && response.data._issues && response.data._issues.name && response.data._issues.name.unique) {
                        scope._errorUniqueness = true;
                    } else {
                        scope._error = true;
                    }
                    scope.message = null;
                }

                function clearErrorMessages() {
                    if (scope._errorUniqueness || scope._error || scope._errorLimits) {
                        scope._errorUniqueness = null;
                        scope._error = null;
                        scope._errorLimits = null;
                    }
                }

                scope.handleEdit = function($event) {
                    clearErrorMessages();
                    if (scope.desk.edit.name != null) {
                        scope._errorLimits = scope.desk.edit.name.length > scope.limits.desk ? true : null;
                    }
                };

            }
        };
    }])
    .directive('sdDeskeditStages', ['gettext', 'api', 'WizardHandler', 'tasks',
        function(gettext, api, WizardHandler, tasks) {
        return {

            link: function(scope, elem, attrs) {

                var orig = null;

                scope.limits = limits;

                scope.statuses = tasks.statuses;

                scope.$watch('step.current', function(step, previous) {
                    if (step === 'stages') {
                        scope.editStage = null;
                        orig = null;
                        scope.stages = [];
                        scope.selected = null;
                        scope.message = null;

                        if (scope.desk.edit && scope.desk.edit._id) {
                            scope.message = null;
                            api('stages').query({where: {desk: scope.desk.edit._id}})
                            .then(function(result) {
                                scope.stages = result._items;
                            });
                        } else {
                            WizardHandler.wizard('desks').goTo(previous);
                        }
                    }
                });

                scope.previous = function() {
                    WizardHandler.wizard('desks').previous();
                };

                scope.next = function() {
                    WizardHandler.wizard('desks').next();
                };

                scope.edit = function(stage) {
                    if (stage.is_visible == null) {
                        stage.is_visible = true;
                    }

                    orig = stage;
                    scope.editStage = _.create(stage);
                    if (!scope.editStage._id) {
                        var lastStage = _.last(scope.stages);
                        if (lastStage) {
                            scope.editStage.task_status = lastStage.task_status;
                        }
                    }
                };

                scope.isActive = function(stage) {
                    return scope.editStage && scope.editStage._id === stage._id;
                };

                scope.cancel = function() {
                    scope.editStage = null;
                    clearErrorMessages();
                };

                scope.select = function(stage) {
                    if (scope.editStage && scope.editStage._id !== stage._id) {
                        return false;
                    }

                    scope.selected = stage;
                };

                scope.setStatus = function(status) {
                    scope.editStage.task_status = status._id;
                };

                scope.save = function() {
                    if (!orig._id) {
                        _.extend(scope.editStage, {desk: scope.desk.edit._id});
                        api('stages').save({}, scope.editStage)
                        .then(function(item) {
                            scope.stages.push(item);
                            scope.editStage = null;
                            scope.select(item);
                            scope.message = null;
                        }, errorMessage);
                    } else {
                        api('stages').save(orig, scope.editStage)
                        .then(function(item) {
                            scope.editStage = null;
                            scope.message = null;
                            scope.select(item);
                        }, errorMessage);
                    }
                };

                function errorMessage(response) {
                    if (response.data && response.data._issues && response.data._issues.name && response.data._issues.name.unique) {
                        scope._errorUniqueness = true;
                    } else {
                        scope._error = true;
                    }
                    scope.message = null;
                }

                scope.handleEdit = function($event) {
                    clearErrorMessages();
                    if (scope.editStage.name != null) {
                        scope._errorLimits = scope.editStage.name.length > scope.limits.stage ? true : null;
                    }
                };

                function clearErrorMessages() {
                    if (scope._errorUniqueness || scope._error || scope._errorLimits) {
                        scope._errorUniqueness = null;
                        scope._error = null;
                        scope._errorLimits = null;
                    }
                }

                scope.remove = function(stage) {
                    api('stages').remove(stage)
                    .then(function() {
                        if (stage === scope.selected) {
                            scope.selected = null;
                        }
                        _.remove(scope.stages, stage);
                        scope.message = null;
                    }, function(result) {
                        scope.message = gettext('There was a problem, stage was not deleted.');
                    });
                };
            }
        };
    }])
    .directive('sdUserSelectList', ['$filter', 'api', function($filter, api) {
        return {
            scope: {
                exclude: '=',
                onchoose: '&'
            },
            templateUrl: 'scripts/superdesk-desks/views/user-select.html',
            link: function(scope, elem, attrs) {

                var ARROW_UP = 38, ARROW_DOWN = 40, ENTER = 13;

                scope.selected = null;
                scope.search = null;
                scope.users = {};
                scope.exclude = [];

                var _refresh = function() {
                    scope.users = {};
                    return api('users').query({where: JSON.stringify({
                        '$or': [
                            {username: {'$regex': scope.search, '$options': '-i'}},
                            {first_name: {'$regex': scope.search, '$options': '-i'}},
                            {last_name: {'$regex': scope.search, '$options': '-i'}},
                            {email: {'$regex': scope.search, '$options': '-i'}}
                        ]
                    })})
                    .then(function(result) {
                        scope.users = result;
                        scope.users._items = _.filter(scope.users._items, function(item) {
                            return _.findIndex(scope.exclude, {_id: item._id}) === -1;
                        });
                        scope.selected = null;
                    });
                };
                var refresh = _.debounce(_refresh, 1000);

                scope.$watch('search', function() {
                    if (scope.search) {
                        refresh();
                    }
                });

                function getSelectedIndex() {
                    if (scope.selected) {
                        return _.findIndex(scope.users._items, scope.selected);
                    } else {
                        return -1;
                    }
                }

                function previous() {
                    var selectedIndex = getSelectedIndex();
                    if (selectedIndex > 0) {
                        scope.select(scope.users._items[_.max([0, selectedIndex - 1])]);
                    }
                }

                function next() {
                    var selectedIndex = getSelectedIndex();
                    scope.select(scope.users._items[_.min([scope.users._items.length - 1, selectedIndex + 1])]);
                }

                elem.bind('keydown keypress', function(event) {
                    scope.$apply(function() {
                        switch (event.which) {
                            case ARROW_UP:
                                event.preventDefault();
                                previous();
                                break;
                            case ARROW_DOWN:
                                event.preventDefault();
                                next();
                                break;
                            case ENTER:
                                event.preventDefault();
                                if (getSelectedIndex() >= 0) {
                                    scope.choose(scope.selected);
                                }
                                break;
                        }
                    });
                });

                scope.choose = function(user) {
                    scope.onchoose({user: user});
                    scope.search = null;
                };

                scope.select = function(user) {
                    scope.selected = user;
                };
            }
        };
    }])
    .directive('sdDeskeditPeople', ['gettext', 'WizardHandler', 'desks',
        function(gettext, WizardHandler, desks) {
        return {
            link: function(scope, elem, attrs) {

                scope.$watch('step.current', function(step, previous) {
                    if (step === 'people') {
                        scope.search = null;
                        scope.deskMembers = [];
                        scope.message = null;

                        if (scope.desk.edit && scope.desk.edit._id) {
                            desks.fetchUsers().then(function(result) {
                                scope.users = desks.users._items;
                                scope.deskMembers = desks.deskMembers[scope.desk.edit._id] || [];
                            });
                        } else {
                            WizardHandler.wizard('desks').goTo(previous);
                        }
                    }
                });

                scope.add = function(user) {
                    scope.deskMembers.push(user);
                };

                scope.remove = function(user) {
                    _.remove(scope.deskMembers, user);
                };

                scope.previous = function() {
                    WizardHandler.wizard('desks').previous();
                };

                scope.save = function() {
                    var members = _.map(scope.deskMembers, function(obj) {
                        return {user: obj._id};
                    });

                    desks.save(scope.desk.edit, {members: members}).then(function(result) {
                        _.extend(scope.desk.edit, result);
                        desks.deskMembers[scope.desk.edit._id] = scope.deskMembers;
                        var origDesk = desks.deskLookup[scope.desk.edit._id];
                        _.extend(origDesk, scope.desk.edit);
                        WizardHandler.wizard('desks').finish();
                    }, function(response) {
                        scope.message = gettext('There was a problem, members not saved.');
                    });
                };
            }
        };
    }])
    .directive('sdDeskstagepicker', ['desks', function(desks) {
        return {
            scope: {
                desk: '=',
                stage: '='
            },
            templateUrl: 'scripts/superdesk-desks/views/deskstagepicker.html',
            link: function(scope, elem, attrs) {
                scope.desks = null;
                scope.deskStages = null;

                scope.$watchGroup(['desk', 'stage'], function() {
                    if (!scope.desks || !scope.deskStages) {
                        desks.initialize()
                        .then(function() {
                            scope.desks = desks.desks._items;
                            scope.deskStages = desks.deskStages;
                        });
                    } else if (scope.desk && _.findIndex(scope.deskStages[scope.desk], {_id: scope.stage}) === -1) {
                        scope.stage = null;
                    }
                });
            }
        };
    }])
    .directive('sdDeskMacros', ['macros', function (macros) {
        return {
            link: function(scope) {
                if (scope.desk && scope.desk.edit) {
                    macros.getByDesk(scope.desk.edit.name).then(function(macros) {
                        scope.macros = macros;
                    });
                }
            }
        };
    }]);
});
