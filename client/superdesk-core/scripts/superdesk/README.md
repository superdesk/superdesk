# Superdesk core

This is group of modules which provide basic functionality for building superdesk apps:

- activity
- api
- auth
- beta
- config
- datetime
- elastic
- error
- list
- notify
- upload

### Module structure

Each module contains a file with same name as module folder - eg `activity/activity.js`.

This is where it's registered via `angular.module` using name like `superdesk.activity`,
and it requires different components there which are located within folder, each in its
own file with `-type.js` suffix (`reldate-directive.js`).

#### Views

Views are saved within `views` folder in module (`activity/views`). When setting a `templateUrl`
use `require.toUrl` with relative path to `views` folder.
