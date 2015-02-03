# Contributing to superdesk client

Great you got here! Please follow the guidelines to ease the process of accepting the changes.

## Test your code

Please write tests whenever it makes sense and make sure the existing tests pass. You can use `grunt` task for this:

```
grunt test
```

will run all the existing test using `_spec.js` convetion.

## Check code style

We use `jshint` and `jscs` to ensure we're all on same page regarding code style. There are `grunt` tasks:

    grunt jshint
    grunt jscs

which runs those respective checkers.

You can also use `grunt ci` which runs both + unit tests all together (used by `travis-ci`).

## Use recommended modules/submodules/apps structure

There are 2 main areas - `superdesk core modules` and `superdesk apps`.

### Superdesk core module structure

In `superdesk core` we split by feature into submodules like `superdesk/upload` where there is an `upload.js` file which defines `superdesk.upload` angular module. This file can via require load its components (directives, controllers, services) but all the angular registration should happen in `upload.js`.

We put most of components into root submodule dir with a type suffix - `upload-service.js` - and with unit tests next to with a `_spec.js` suffix - `upload-service_spec.js`.

Views are put into views subfolder and referenced using `require.toUrl`:

```javascript
// upload-directive.js
define(['require'], function(require) {
    'use strict';
    
    return function() {
        return {
            templateUrl: require.toUrl('./views/upload-directive.html'),
            ...
        };
    };
});
```

### Superdesk apps module

There is always a base module file `module.js` inside of the app folder which returns an angular module which has all the app components registered. Inside of the app it should be structured like in the superdesk core modules.
