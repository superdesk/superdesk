define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope',
        function($scope) {

			$scope.desks = [
				{
					name : 'Culture',
					members : [
						{
							name : 'Paco González'
						},
						{
							name : 'Matina Stevis'
						},
						{
							name : 'April O\'Neil'
						}
					],
					cards : [
						{
							name : 'To Do',
							limit : 50,
							color : 1,
							statuses : [
								{
									key : 'created'
								},
								{
									key : 'just added'
								},
								{
									key : 'breaking'
								}
							]
						},
						{
							name : 'In progress',
							limit : 10,
							color : 2,
							statuses : [
								{
									key : 'in progress'
								},
								{
									key : 'writing'
								}
							]
						},
						{
							name : 'In progress',
							limit : 300,
							color : 3,
							statuses : [
								{
									key : 'done'
								},
								{
									key : 'finished'
								}
							]
						}
					],
					statuses : [
						{
							key : 'created'
						},
						{
							key : 'just added'
						},
						{
							key : 'breaking'
						},
						{
							key : 'in progress'
						},
						{
							key : 'writing'
						},
						{
							key : 'finished'
						},
						{
							key : 'in review'
						},
						{
							key : 'done'
						}
					]
				},
				{
					name : 'Politics',
					members : [],
					cards : [],
					taskstatuses : []
				},
				{
					name : 'Sport',
					members : [],
					cards : [],
					taskstatuses : []
				}
			];

			$scope.edit = function(desk) {
				if (desk === null || desk === undefined) {
					$scope.editDesk = {
						name : null,
						members : [],
						cards : [],
						taskstatuses : []
					};
				}
				else {
					$scope.editDesk = desk;
				}
			};

			$scope.cancel = function() {
				$scope.editDesk = null;
			};

			$scope.save = function() {
				$scope.desks.push($scope.editDesk);
				$scope.cancel();
			};
		}];
});