import {startApp} from 'superdesk-core/scripts/index';

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
                id: 'broadcasting',
                load: () => import('superdesk-core/scripts/extensions/broadcasting').then((broadcasting) => {
                    broadcasting.setCustomizations({
                        getRundownItemDisplayName: (rundown) => rundown.technical_title,
                    });

                    return broadcasting;
                }),
            },
            {
                id: 'ai-widget',
                load: () => import('superdesk-core/scripts/extensions/ai-widget').then((ext) => {
                    // Documentation instance (SDESK-8055): canned answers for the AI screenshots, copied from
                    // the client-core e2e patch in superdesk-docs-user-guide/tools/screenshots. No AI service
                    // is called.
                    ext.configure(() => ({
                        generateHeadlines: () => Promise.resolve([
                            'Coalition budget promises tax relief for 1.2 million households',
                            'Election budget cuts family income tax and adds levy on holiday rentals',
                            'Opposition questions how coalition will pay for pre-election tax cuts',
                        ]),
                        generateSummary: () => Promise.resolve(
                            'The governing coalition presented an election-year budget that cuts income tax for '
                            + 'about 1.2 million households. Finance Minister Ilse Marrow said a new levy on '
                            + 'short-term rentals and a freeze on defence spending would pay for it. The opposition '
                            + 'Civic Union said the levy would raise less than half of the 900 million crowns the '
                            + 'government expects.',
                        ),
                        translations: {
                            generateTranslations: () => Promise.resolve(
                                '<p>Die Regierungskoalition hat am Montag einen Wahlhaushalt vorgestellt, der die '
                                + 'Einkommensteuer für rund 1,2 Millionen Haushalte senkt.</p><p>Finanzministerin '
                                + 'Ilse Marrow sagte, die Entlastung werde durch eine neue Abgabe auf '
                                + 'Kurzzeitvermietungen finanziert.</p>',
                            ),
                            translateActionIntegration: false,
                        },
                    }));

                    return ext;
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
            {
                id: 'content-lists',
                load: () => import('superdesk-core/scripts/extensions/content-lists'),
            },
            // extensions:end
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
