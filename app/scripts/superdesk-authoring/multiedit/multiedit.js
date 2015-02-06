/**
 * This file is part of Superdesk.
 *
 * Copyright 2015 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */
 (function() {

	'use strict';

	MultieditService.$inject = ['storage', 'superdesk'];
	function MultieditService(storage, superdesk) {

		//1. Service manages multiedit screen
		//2. Screen has it's boards, at least 2 of them
		//3. Every board can be popuplated with one content item

		var MIN_BOARDS = 2;
		var STORAGE_KEY = 'multiedit';

		var saved = storage.getItem(STORAGE_KEY);
		this.items = saved === null ? [] : saved;

		this.create = function(_ids) {
			var self = this;
			self.items = [];

			if (_ids) {
				_.each(_ids, function(_id) {
					self.items.push(createBoard(_id));
				});
			}
			if (self.items.length < MIN_BOARDS) {
				for (var i = 0; i < (MIN_BOARDS - self.items.length); i++) {
					self.items.push(createBoard(null));
				}
			}

			self.updateItems();
			self.open();
		};

		this.close = function(item) {
			this.items = [];
			this.updateItems();
		};

		this.open = function() {
			superdesk.intent('author', 'multiedit');
		};

		this.updateItems = function() {
			storage.setItem(STORAGE_KEY, this.items);
		};

		function createBoard(_id) {
			return {article: _id};
		}
	}

	MultieditController.$inject = ['$scope', 'multiEdit'];
	function MultieditController($scope, multiEdit) {

		$scope.screen = multiEdit.items;

	}

	MultieditDropdownDirective.$inject = ['workqueue', 'multiEdit', '$route'];
	function MultieditDropdownDirective(workqueue, multiEdit, $route) {
		return {
			templateUrl: 'scripts/superdesk-authoring/multiedit/views/sd-multiedit-dropdown.html',
			link: function(scope) {

				scope.current = $route.current.params._id;
				scope.queue = [scope.current];

				scope.$watch(function () {
					return workqueue.items;
				}, function(items) {
					scope.items = items;
				}, true);

				scope.toggle = function(_id) {
					if (_id === scope.current) {
						return false;
					}
					if (scope.selected(_id)) {
						scope.queue = _.without(scope.queue, _id);
					} else {
						scope.queue.push(_id);
					}
				};

				scope.selected = function(_id) {
					return _.indexOf(scope.queue, _id) !== -1;
				};

				scope.open = function() {
					multiEdit.create(scope.queue);
				};
			}
		};
	}

	MultieditArticleDirective.$inject = ['authoring'];
	function MultieditArticleDirective(authoring) {
		return {
			template: '<div sd-article-edit></div>',
			scope: {article: '='},
			link: function(scope) {
				authoring.open(scope.article).then(function(item) {
					scope.item = _.create(item);
					scope._editable = authoring.isEditable(item);
				});

                scope.autosave = function(item) {
                    scope.dirty = true;
                    authoring.autosave(item);
                };

				scope.save = function(item) {
					return authoring.save(item);
				};
			}
		};
	}

	angular.module('superdesk.authoring.multiedit', ['superdesk.activity', 'superdesk.authoring'])
		.service('multiEdit', MultieditService)
		.directive('sdMultieditDropdown', MultieditDropdownDirective)
		.directive('sdMultieditArticle', MultieditArticleDirective)

		.config(['superdeskProvider', function(superdesk) {
			superdesk
				.activity('multiedit', {
					category: '/authoring',
					href: '/multiedit',
					when: '/multiedit',
					label: gettext('Authoring'),
					templateUrl: 'scripts/superdesk-authoring/multiedit/views/multiedit.html',
					topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
					controller: MultieditController,
					filters: [{action: 'author', type: 'multiedit'}]
				});
		}]);
})();
