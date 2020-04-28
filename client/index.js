import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [],
        {},
    );
});

export default angular.module('main.superdesk', []);
