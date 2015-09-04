# Superdesk lib
This documentation is targeted at superdesk developers and developers in general who want to use superdesk as part of their project. It describes steps how to write your own superdesk app plus the key concepts.
Term `superdesk` here will refer to the core lib of the framework, located in `app/scripts/superdesk`, which will be released as a standalone library in the future.

### How to write an app using superdesk
Every app is an angular module, with some config blocks that register app components and thus make them available to other apps and the framework.
```js
var app = angular.module('myApp', ['superdesk']);
```

There are 2 components an app can provide at the moment:
- dashboard `widgets`
- `activities`

#### Widgets
Widget is a component that can be rendered on user dashboard.

```js
app.config(['superdeskProvider', function(superdeskProvider) {
    superdeskProvider.widget('myWidget', {
        label: 'MyWidget', // string
        multiple: true, // boolean - can user have more such widgets at a time (with different config)
        icon: 'info', // string - `icon-` class
        thumbnail: 'scripts/my-app/images/thumbnail.png', // url for thumbnail image
        template: 'scripts/my-app/views/widget.html', // url for widget template
        description: 'My Widget long description', // string
        configuration: {max: 5}, // Object - default config for widget
        configurationTemplate: 'scripts/my-app/views/config.html', // url for config template
        max_sizex: 2, // integer - max horizontal size (2 of 4x4 dashboard),
        max_sizey: 2, // integer - max vertical size
        sizex: 1, // integer - default horizontal size
        sizey: 1, // integer - default vertical size
    });
}]);
```

#### Activity
Activity can be displayed in a main menu, or be triggered from other apps when needed. You can also override existing activities for given action.

##### Register Main menu activity
```js
app.config(['superdeskProvider', function(superdeskProvider) {
    superdeskProvider.activity('myActivity', {
        label: gettext('My App Dashboard'),
        category: superdeskProvider.MENU_MAIN
    });
}]);
```

##### Register activity for certain action
To specify what your activity can do, you can define intent filters:

```js
app.config(['superdeskProvider', function(superdeskProvider) {
    superdeskProvider.activity('mySendActivity', {
        label: gettext('Send'),
        filters: [
            {action: 'send', type: 'picture'}
        ]
    });
}]);
```

Each filter has `action` and data `type` which is used to pick the appropriate activity.

#### Intent
When you want to start an `activity` out of your app, you have to create an `intent` for it. There you specify `action` you want to perform with data and superdesk will resolve it to an `activity` which can handle it. In case there are multiple `activities` for the task user will be presented with a dialog where he can choose one.

```js
app.controller(function($scope, superdesk) {
    $scope.send = function(item) {
        superdesk.intent('send', item);
    };
});
```

## Superdesk API
@ todo generate docs for:
- `superdesk` component registry
- `data` rest api adapter
- `keyboard` keyboard bindings manager
- `notify` notification service
- `storage` local storage adapter
- `translate` gettext adapter
