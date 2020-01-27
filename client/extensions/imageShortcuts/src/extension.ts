import {ISuperdesk, IExtension, IExtensionActivationResult, IArticle} from 'superdesk-api';
import {getWidgets} from './get-widgets';

const extension: IExtension = {
    id: 'image-shortcuts',
    activate: (superdesk: ISuperdesk) => {
        // expose API method via a global so angularjs code can use it.
        (window as any)['__private_ansa__add_image_to_article'] = (field: string, image: IArticle) => {
            // call the original method from within the extension so usages can be tracked easily
            superdesk.ui.article.addImage(field, image);
        };

        (window as any)['__private_ansa__get_content_profile'] = (id: string) => {
            // call the original method from within the extension so usages can be tracked easily
            return superdesk.entities.contentProfile.get(id);
        };

        const result: IExtensionActivationResult = {
            contributions: {
                articleListItemWidgets: [getWidgets(superdesk)],
                articleGridItemWidgets: [getWidgets(superdesk)],
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
