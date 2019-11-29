import {IExtension, IExtensionActivationResult, ISuperdesk, IArticle, ISubject} from 'superdesk-api';

const PHOTO_CATEGORIES_ID = 'PhotoCategories';
const parseDate = (date: string, time: string) => (date && time)
    ? (date.split('-').join('') + 'T' + time.split(':').join(''))
    : null;

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                iptcMapping: (data, item: IArticle) => Promise.all([
                    superdesk.entities.vocabulary.getIptcSubjects(),
                    superdesk.entities.vocabulary.getVocabulary(PHOTO_CATEGORIES_ID),
                ]).then(([subjects, categories]: [Array<ISubject>, Array<ISubject>]) => {
                    const subjectReference = Array.isArray(data.SubjectReference) ? data.SubjectReference : [data.SubjectReference || ''];

                    Object.assign(item, {
                        slugline: data.ObjectName,
                        byline: data['By-line'],
                        sign_off: data['By-lineTitle'] || item.sign_off,
                        headline: data.Headline,
                        source: data.Source,
                        copyrightholder: data.Credit,
                        copyrightnotice: data.CopyrightNotice,
                        usageterms: data.CopyrightNotice,
                        language: data.LanguageIdentifier || 'it',
                        subject: (item.subject || []).concat(
                            subjects.filter((subj) => subjectReference.find((ref) => ref.includes(subj.qcode))),
                            data.Category != null ?
                                categories.filter((cat) => cat.name === data.Category)
                                    .map((cat) => ({name: cat.name, qcode: cat.qcode, scheme: PHOTO_CATEGORIES_ID})) :
                                [],
                        ),
                        extra: {
                            city: data.City,
                            nation: data['Country-PrimaryLocationName'],
                            digitator: data['Writer-Editor'],
                            DateCreated: parseDate(data.DateCreated, data.TimeCreated),
                            DateRelease: parseDate(data.ReleaseDate, data.ReleaseTime),
                        },
                    });

                    return item;
                }),
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
