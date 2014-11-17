
(function() {

'use strict';

MetadataCtrl.$inject = ['$scope', 'desks', 'metadata', '$filter'];
function MetadataCtrl($scope, desks, metadata, $filter) {
	desks.initialize()
	.then(function() {
		$scope.deskLookup = desks.deskLookup;
		$scope.userLookup = desks.userLookup;
	});

	metadata.initialize().then(function() {
		$scope.metadata = metadata.values;
	});
}

MetadataDropdownDirective.$inject = [];
function MetadataDropdownDirective() {
	return {
		scope: {
			list: '=',
			disabled: '=',
			item: '=',
			field: '@'
		},
		templateUrl: 'scripts/superdesk-authoring/metadata/views/metadata-dropdown.html',
		link: function(scope) {
			scope.select = function(item) {
				scope.item = scope.field ? item[scope.field] : item;
			};
		}
	};
}

MetadataListEditingDirective.$inject = [];
function MetadataListEditingDirective() {
	return {
		scope: {
			item: '=',
			disabled: '=',
			field: '@',
			list: '='
		},
		templateUrl: 'scripts/superdesk-authoring/metadata/views/metadata-terms.html',
		link: function(scope) {

			scope.terms = [];
			scope.selectedTerm = '';

			scope.searchTerms = function(term) {
				if (!term) {
					scope.terms = [];
				} else {
					scope.terms = _.filter(scope.list, function(t) {
					return ((t.name.toLowerCase().indexOf(term.toLowerCase()) !== -1) &&
					!_.find(scope.item[scope.field], {qcode: t.qcode}));
					});
				}

				return scope.terms;
			};

			scope.selectTerm = function(term) {
				if (term) {

					//instead of simple push, extend the item[field] in order to trigger dirty $watch
					var t = _.clone(scope.item[scope.field]) || [];
					t.push(term);

					//build object
					var o = {};
					o[scope.field] = t;
					_.extend(scope.item, o);

					scope.selectedTerm = '';
				}
			};

			scope.removeTerm = function(term) {
				var temp = _.without(scope.item[scope.field], term);

				//build object
				var o = {};
				o[scope.field] = temp;

				_.extend(scope.item, o);
			};
		}
	};
}

MetadataService.$inject = ['api', '$q', 'metadataMock'];
function MetadataService(api, $q, metadataMock) {

	var service = {
		values: {},
		loaded: null,
		fetchMetadataValues: function() {
			var self = this;

			_.each(metadataMock, function(val) {
				self.values[val._id] = val._items;
			});

			return $q.when();
		},
		fetchSubjectcodes: function(code) {
			var self = this;
			return api.get('/subjectcodes').then(function(result) {
				self.values.subjectcodes = result._items;
			});
		},
		initialize: function() {
			if (!this.loaded) {
				this.loaded = this.fetchMetadataValues()
					.then(angular.bind(this, this.fetchSubjectcodes));
			}
			return this.loaded;
		}
	};

	return service;
}

//just for mocking purpose - will be replcaed by API call
var metadataMock = [
	{
		_id: 'categories',
		_items: [
			{
				name: 'Domestic, non-Washington, general news item',
				qcode: 'A'
			},
			{
				name: 'Special Events. National tabular election items',
				qcode: 'B'
			},
			{
				name: 'International news, including United Nations and undated roundups keyed to foreign events',
				qcode: 'I'
			}
		]
	},
	{
		_id: 'newsvalues',
		_items: [
			{
				name: '1',
				qcode: 1
			},
			{
				name: '2',
				qcode: 2
			},
			{
				name: '3',
				qcode: 3
			}
		]
	},
	{
		_id: 'priority',
		_items: [
			{
				name: 'B',
				qcode: 'B'
			},
			{
				name: 'D',
				qcode: 'D'
			},
			{
				name: 'F',
				qcode: 'F'
			}
		]
	},
	{
		_id: 'genre',
		_items: [
			{
				qcode: 'exclusive',
				name: 'Exclusive'
			},
			{
				qcode: 'profile',
				name: 'Profile'
			},
			{
				qcode: 'wrapup',
				name: 'Wrapup'
			}
		]
	},
	{
		_id: 'placecodes',
		_items: [
			{
				qcode: '12345',
				name: 'Sydney, AU'
			},
			{
				qcode: '54321',
				name: 'Belgrade, SR'
			},
			{
				qcode: '00987',
				name: 'Prague, CZ'
			}
		]
	}
];
angular.module('superdesk.authoring.metadata', ['superdesk.authoring.widgets'])
	.config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
		authoringWidgetsProvider
			.widget('metadata', {
				icon: 'info',
				label: gettext('Info'),
				template: 'scripts/superdesk-authoring/metadata/views/metadata-widget.html',
				order: 1
			});
	}])

	.controller('MetadataWidgetCtrl', MetadataCtrl)
	.service('metadata', MetadataService)
	.directive('sdMetaTerms', MetadataListEditingDirective)
	.directive('sdMetaDropdown', MetadataDropdownDirective)
	.value('metadataMock', metadataMock);
})();
