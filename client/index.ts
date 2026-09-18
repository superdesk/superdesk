import {startApp} from 'superdesk-core/scripts/index';
import {configureAiWidget} from './briefdesk/ai-actions';

setTimeout(() => {
    startApp(
        [
            // Always-on / manually-managed extensions. Entries with custom load
            // logic (.then, setCustomizations) live here so scripts/dev/extension.sh
            // can manipulate the standard-template region below without worrying
            // about them.
            {
                id: 'planning-extension',
                load: () => import('superdesk-planning/client/planning-extension'),
            },
            {
                // The id has to stay 'ai-widget': the extension reads its API instance out of
                // window.extensionsApiInstances under that key.
                id: 'ai-widget',
                load: () => import('superdesk-core/scripts/extensions/ai-widget').then((aiWidget) => {
                    aiWidget.configure(configureAiWidget);

                    return aiWidget;
                }),
            },

            // extensions:start (managed by scripts/dev/extension.sh — do not edit by hand)
            {
                id: 'annotationsLibrary',
                load: () => import('superdesk-core/scripts/extensions/annotationsLibrary'),
            },
            {
                id: 'markForUser',
                load: () => import('superdesk-core/scripts/extensions/markForUser'),
            },
            {
                id: 'datetimeField',
                load: () => import('superdesk-core/scripts/extensions/datetimeField'),
            },
            {
                id: 'availability-manager',
                load: () => import('superdesk-core/scripts/extensions/availability-manager'),
            },
            // extensions:end
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
