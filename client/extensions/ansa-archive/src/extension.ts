import {IExtension, IExtensionActivationResult, ISuperdesk, IArticle, IArticleActionBulk} from 'superdesk-api';

const isExternalPicture = (article: IArticle) =>
    article._type === 'externalsource' &&
    article.fetch_endpoint === 'search_providers_proxy';

const extension: IExtension = {
    id: 'ansa-archive',
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                entities: {
                    article: {
                        getActionsBulk: (articles) => {
                            const actions: Array<IArticleActionBulk> = [];

                            if (articles.every(isExternalPicture)) {
                                actions.push({
                                    icon: 'icon-trash',
                                    label: superdesk.localization.gettext('Delete'),
                                    onTrigger: () => {
                                        Promise.all(articles.map((article) => {
                                            return superdesk.dataApi.delete('ansa_archive', article);
                                        })).then(() => {
                                            superdesk.ui.alert(superdesk.localization.gettext('Items were removed.'));
                                        }).catch(() => {
                                            superdesk.ui.alert(superdesk.localization.gettext('There was an error.'));
                                        });
                                    },
                                });
                            }

                            return Promise.resolve(actions);
                        },
                    },
                },
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
