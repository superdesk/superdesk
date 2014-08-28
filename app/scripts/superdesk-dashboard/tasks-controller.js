define(['lodash'], function(_) {
    'use strict';

    TasksController.$inject = ['$scope'];
    function TasksController($scope) {

        $scope.selected = {};

        $scope.tasks = [
            {
                _id: '12345679asdfghjk',
                title: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
                description: 'Sed ut perspiciatis unde omnis iste natus error sit voluptatem ' +
                ' accusantium doloremque laudantium,totam rem aperiam, eaque ipsa quae ab illo ' +
                ' inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo',
                duedate: '2014-11-11T12:12:12+01:00',
                assigned_user: '5399826e1024543327ebfafa',
                status: 1
            },
            {
                _id: '12aiouadm5679ajk',
                title: 'At vero eos et accusamus et iusto odio dignissimos',
                description: 'O inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo',
                duedate: '2014-12-11T12:12:12+01:00',
                assigned_user: '53fca4be1024542d4db4b588',
                status: 1
            },
            {
                _id: 'q1w2e3r4t5dfsdfsdhjk',
                title: 'necessitatibus saepe eveniet ut et voluptates repudiandae',
                description: 'Ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores' +
                'et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui' +
                ' officia deserunt mollitia animi',
                duedate: '2014-11-12T12:12:12+01:00',
                assigned_user: '53739e771024540be78f178a',
                status: 2
            }
        ];

        $scope.preview = function(item) {
            $scope.selected.preview = item;
        };
    }

    return TasksController;
});
