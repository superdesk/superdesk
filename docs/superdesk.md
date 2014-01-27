# Superdesk Dev Docs

This documentation is targeted at superdesk developers and developers in general who want to use superdesk as part of their project. It describes key concepts and steps how to create your own superdesk app. Term `superdesk` here will refer to the core of the framework, located in ```app/scripts/superdesk```, which will be released as a superdesk library at some point.

## Concepts

The core of `superdesk` is based on `intents` and `activities` (inspired by android).

### Activity

In order to implement some functionality, you define an `activity` which you have to register via `superdeskProvider`.
It is a wrapper on top of `ngRoute` so all its params work there, but also you can define filters which will make activity available for other apps.

### Intent

When you want to start an `activity`, you have to create an `intent` for it. There you specify `action` you want to perform with data and superdesk will resolve it an `activity` which can handle it. In case there are multiple `activities` for the task user will be presented with a dialog where he can choose one.

## How to make an app

Your app must be an angular module, which will use `superdeskProvider` to register its components, and it can use `superdesk` service, but also other angular services/modules.

So first we start creating an app which we will use later on.

```
var app = angular.module('myApp', ['superdesk']);
```

### Registering main menu item
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

### Using Superdesk for data access
There is a superdesk data adapter which provides access for superdesk rest api server. It handles authentication and provides an auto update when query criteria change for given query.

```
app.controller(['$scope', 'superdesk', function($scope, superdesk) {
    $scope.data = superdesk.data('users', {max_results: 25});
}]);
```
