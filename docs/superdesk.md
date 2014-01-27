* Superdesk Dev Docs
This documentation is targeted at superdesk developers and developers in general who want to use superdesk as part of their project. It describes key concepts and
steps how to create your own superdesk app.

** Overview
Superdesk is a js client, build on top of ```angularjs```, ```requirejs```, ```jquery```, ```bootstrap``` and other technologies.

** How to make an app
Your app must be an angular module, which will use superdesk providers to register its components, and it can use superdesk services to implement required functionality.

```
var app = angular.module('myApp', ['superdesk']);
```

*** Registering main menu item
In order to register a main menu item, your app must define an activity with ```superdesk.MENU_MAIN``` category.

```
app.config(['superdeskProvider', function(superdesk) {
    superdesk.activity('foo', {
        label: 'MyApp',
        controller: 'MyAppCtrl',
        templateUrl: 'scripts/my-app/views/my-app.html',
        category: superdesk.MENU_MAIN
    });
}]);
```

*** Using Superdesk for data access
There is a superdesk data adapter which provides access for superdesk rest api server. It handles authentication and provides an auto update when query criteria change for given query.

```
app.controller(['$scope', 'superdesk', function($scope, superdesk) {
    $scope.data = superdesk.data('users', {max_results: 25});
}]);
```
