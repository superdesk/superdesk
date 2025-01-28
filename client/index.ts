import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [
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
        ],
        {},
        {
            editor3: {
                customBlocks: {
                    getAdditionalWrapperAttributes: (_vocabulary, html) => {
                        function getHighestHeadingText(el: HTMLElement): string | null {
                            const headings: Array<keyof HTMLElementTagNameMap> = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'];

                            for (const tag of headings) {
                                const result = el.querySelector(tag);

                                if (result != null) {
                                    return result.textContent;
                                }
                            }

                            return null;
                        }

                        const tableCellContentElement: HTMLElement =
                            new DOMParser().parseFromString(html, 'text/html').body;

                        const replaceSpecialCharacters = (str) =>
                            str.normalize('NFD').replace(/[\u0300-\u036f]/g, '') // Remove accents
                                .replace(/([^\w]+|\s+)/g, '-') // Replace space and other characters by hyphen
                                .replace(/\-\-+/g, '-')	// replace multiple hyphens with one hyphen
                                .replace(/(^-+|-+$)/g, ''); // remove extra hyphens from beginning or end of the string

                        const heading: string | null = getHighestHeadingText(tableCellContentElement);

                        const attributes: Array<{name: string; value: string}> = [
                            {name: 'class', value: 'custom-block'},
                        ];

                        if (heading != null) {
                            attributes.push({name: 'data-custom-block-title', value: replaceSpecialCharacters(heading).toLocaleLowerCase()});
                        }

                        return attributes;
                    },
                },
            },
        },
    );
});

export default angular.module('main.superdesk', []);
