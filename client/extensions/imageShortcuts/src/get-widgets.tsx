import * as React from 'react';
import {ISuperdesk, IArticle, IContentProfile} from "superdesk-api";

interface IProps {
    article: IArticle;
}

interface IState {
    isDisplayed: boolean;
}

// duplicated in client/ansa/AnsaRelatedCtrl.js
// constants aren't used to avoid imports between multiple projects
export const featureMediaField = 'feature_media';
export const galleryField = 'photoGallery';


// `contentProfile` and `getContentProfilePromise` are shared between multiple instances of `getWidgets` result
// one instance is created for list view and another for grid view. See usages.
let contentProfile: IContentProfile | undefined = undefined;
let getContentProfilePromise: Promise<IContentProfile> | undefined = undefined;

export function getWidgets(superdesk: ISuperdesk) {
    const {Icon} = superdesk.components;
    const {gettext} = superdesk.localization;

    return class extends React.PureComponent<IProps, IState> {
        show: (article: IArticle) => void;
        hide: () => void;

        constructor(props: IProps) {
            super(props);

            this.state = {
                // components can be remounted even if `articleEditStart` /  `articleEditEnd` haven't fired
                // for example if view type is being toggled between list/grid or more items are loaded.
                isDisplayed: typeof contentProfile !== 'undefined',
            };

            this.show = (article: IArticle) => {
                if (article.profile == null) {
                    this.hide();
                    return;
                }

                if (getContentProfilePromise === undefined) {
                    getContentProfilePromise = superdesk.entities.contentProfile.get(article.profile).then((profile) => {
                        if ((profile.schema.hasOwnProperty(featureMediaField) || profile.schema.hasOwnProperty(galleryField))) {
                            contentProfile = profile;
                        }
                        
                        return profile;
                    });
                }

                getContentProfilePromise.then(() => {
                    this.setState({isDisplayed: true});
                });
            };
            this.hide = () => {
                contentProfile = undefined;
                getContentProfilePromise = undefined;

                this.setState({isDisplayed: false});
            };
        }
        componentDidMount() {
            superdesk.addEventListener('articleEditStart', this.show);
            superdesk.addEventListener('articleEditEnd', this.hide);
        }
        componentWillUnmount() {
            superdesk.removeEventListener('articleEditStart', this.show);
            superdesk.removeEventListener('articleEditEnd', this.hide);
        }
        render() {
            if (this.state.isDisplayed !== true || typeof contentProfile === 'undefined') {
                return null;
            }

            if (this.props.article.type === 'picture') {
                return (
                    <div>
                        {
                            contentProfile.schema.hasOwnProperty(galleryField)
                                ? (
                                    <button
                                        title={gettext('add to photo gallery')}
                                        onClick={() => {
                                            superdesk.ui.article.addImage(galleryField, this.props.article);
                                        }}
                                    >
                                        <Icon className="icon-slideshow" size={22} />
                                    </button>
                                )
                                : null
                        }

                        {
                            contentProfile.schema.hasOwnProperty(featureMediaField)
                                ? (
                                    <button
                                        title={gettext('add to featured media')}
                                        onClick={() => {
                                            superdesk.ui.article.addImage(featureMediaField, this.props.article);
                                        }}
                                    >
                                        <Icon className="icon-picture" size={22} />
                                    </button>
                                )
                                : null
                        }
                    </div>
                );
            } else {
                return null;
            }
        }
    }
}
