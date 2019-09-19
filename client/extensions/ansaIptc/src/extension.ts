import {IExtension, IExtensionActivationResult, ISuperdesk} from 'superdesk-api';

const PHOTO_CATEGORIES_ID = 'PhotoCategories';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                iptcMapping: (data, item) => Promise.all([
                    superdesk.entities.vocabulary.getIptcSubjects(),
                    superdesk.entities.vocabulary.getVocabulary(PHOTO_CATEGORIES_ID),
                ]).then(([subjects, categories]) =>
                    Object.assign(item, {
                        usageterms: data.CopyrightNotice,
                        subject: (item.subject || []).concat(
                            data.SubjectReference != null ?
                                subjects.filter((subj) => subj.qcode === data.SubjectReference) :
                                [],
                            data.Category != null ?
                                categories.filter((cat) => cat.name === data.Category)
                                    .map((cat) => ({name: cat.name, qcode: cat.qcode, scheme: PHOTO_CATEGORIES_ID})) :
                                [],
                        ),
                        extra: {
                            city: data.City,
                            nation: data['Country-PrimaryLocationName'],
                        },
                    }),
                ),
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
