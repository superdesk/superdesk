define(['lodash'], function(_) {
    'use strict';

    return ['$scope', 'workspace',
    function ($scope, workspace) {
        $scope.configuration = _.clone($scope.widget.configuration);

        $scope.save = function() {
            $scope.widget.configuration = $scope.configuration;
            workspace.save().then(function() {
                $scope.$close();
            });
        };
    }];
});
