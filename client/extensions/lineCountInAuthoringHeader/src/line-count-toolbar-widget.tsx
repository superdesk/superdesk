import * as React from 'react';

import {IArticle, ISuperdesk} from 'superdesk-api';

export function getLineCountToolbarWidget(superdesk: ISuperdesk) {
    const {gettext, gettextPlural} = superdesk.localization;
    const {getLinesCount, stripHtmlTags} = superdesk.utilities;

    return class LineCountToolbarWidget extends React.PureComponent<{article: IArticle}> {
        render() {
            const {article} = this.props;

            if (article.body_html == null) {
                return null;
            }

            const linesCount = getLinesCount(stripHtmlTags(article.body_html));

            if (linesCount == null) {
                return null;
            }

            return (
                <dl>
                    <dt>{gettext('Line count')}</dt>
                    {' '}
                    <dd>{linesCount} {gettextPlural(linesCount, 'line', 'lines')}</dd>
                </dl>
            );
        }
    }
}