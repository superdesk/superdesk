/**
 * Wires the `ai-widget` extension of superdesk-client-core to the `ai_actions` endpoints of
 * superdesk-core, so its "Headlines" and "Summary" panels run against the configured AI provider.
 *
 * This is demo glue, not the planned authoring integration (SDESK-7996). The widget knows three
 * fixed features and hands the host a callback per feature; everything below exists to turn those
 * callbacks into a run of a stored action.
 */

interface IHttpRequestOptions {
    method: 'GET' | 'POST' | 'PATCH' | 'PUT';
    path: string;
    payload?: {};
    urlParams?: {[key: string]: any};
    abortSignal?: AbortSignal;
}

/** The part of the extension API this file uses. */
interface ISuperdeskApi {
    httpRequestJsonLocal<T>(options: IHttpRequestOptions): Promise<T>;
    ui: {notify: {error(message: string, duration?: number): void}};
}

interface IArticleLike {
    _id: string;
    language?: string;
    [field: string]: any;
}

type IAiActionType = 'suggestion' | 'summary';
type IWidgetFeature = 'headlines' | 'summary';

const ACTION_TYPE_OF_FEATURE: {[key in IWidgetFeature]: IAiActionType} = {
    headlines: 'suggestion',
    summary: 'summary',
};

/**
 * Event id of the latest run per article and action type. The widget reports an applied answer by
 * feature and index only, so the run it belongs to has to be remembered here.
 */
const lastRunEventIds = new Map<string, string>();

function runKey(articleId: string, actionType: IAiActionType): string {
    return `${articleId}:${actionType}`;
}

interface IAiAction {
    _id: string;
    name: string;
    action_type: string;
    active: boolean;
}

interface IRunResponse {
    suggestions: Array<{text: string; over_limit: boolean}>;
    event_id: string;
    provider: string;
    model: string;
}

/**
 * Optional short circuit for the action lookup. Listing `ai_actions` needs the `ai_studio`
 * privilege while running one only needs `ai`, so a user who may run actions but may not configure
 * them cannot look them up by type. Paste the ids here (from the AI Studio settings page or from
 * `GET /api/ai_actions` as an administrator) when the demo users do not hold `ai_studio`.
 */
const ACTION_IDS: {[key in IAiActionType]?: string} = {
    suggestion: '',
    summary: '',
};

/**
 * Item fields whose current text is sent with a run. Anything the action does not list in its own
 * `input_fields` is ignored by the server, and a field left out here falls back to the stored item,
 * so this only has to be a superset of what the Briefdesk actions read.
 */
const INPUT_FIELDS = ['headline', 'slugline', 'abstract', 'body_html'];

function isAbort(error: any): boolean {
    return error != null && (error.name === 'AbortError' || error.code === 20);
}

function readErrorMessage(error: any): string {
    if (typeof error === 'string') {
        return error;
    }

    if (error instanceof Error) {
        return error.message;
    }

    const apiMessage = error?._error?.message ?? error?._message;

    if (typeof apiMessage === 'string' && apiMessage !== '') {
        return apiMessage;
    }

    if (error?._issues != null) {
        return JSON.stringify(error._issues);
    }

    return 'the request to the AI backend failed';
}

function getInputFields(article: IArticleLike): {[field: string]: string} {
    const fields: {[field: string]: string} = {};

    INPUT_FIELDS.forEach((name) => {
        const value = article?.[name];

        if (typeof value === 'string' && value.trim() !== '') {
            fields[name] = value;
        }
    });

    return fields;
}

function resolveActionId(superdesk: ISuperdeskApi, actionType: IAiActionType): Promise<string> {
    const configured = ACTION_IDS[actionType];

    if (typeof configured === 'string' && configured !== '') {
        return Promise.resolve(configured);
    }

    return superdesk
        .httpRequestJsonLocal<{_items?: Array<IAiAction>}>({
            method: 'GET',
            path: '/ai_actions',
            urlParams: {max_results: 200},
        })
        .then((response) => {
            const action = (response._items ?? []).find(
                (candidate) => candidate.active !== false && candidate.action_type === actionType,
            );

            if (action == null) {
                return Promise.reject(
                    new Error(`no active AI action of type "${actionType}" exists on this instance`),
                );
            }

            return action._id;
        });
}

function runAction(
    superdesk: ISuperdeskApi,
    actionType: IAiActionType,
    article: IArticleLike,
    abortSignal: AbortSignal,
): Promise<Array<string>> {
    return resolveActionId(superdesk, actionType)
        .then((actionId) =>
            superdesk.httpRequestJsonLocal<IRunResponse>({
                method: 'POST',
                path: `/ai_actions/${actionId}/run`,
                payload: {
                    item_id: article._id,
                    language: article.language,
                    source: 'authoring',
                    fields: getInputFields(article),
                },
                abortSignal: abortSignal,
            }),
        )
        .then((response) => {
            if (response.event_id != null) {
                lastRunEventIds.set(runKey(article._id, actionType), response.event_id);
            }

            return (response.suggestions ?? []).map((suggestion) => suggestion.text);
        })
        .catch((error) => {
            if (isAbort(error)) {
                return Promise.reject(error);
            }

            const message = `AI assistant: ${readErrorMessage(error)}`;

            // The widget turns any rejection into a bare "there was an error" panel, so the reason
            // is only visible if it is notified here.
            superdesk.ui.notify.error(message, 8000);

            return Promise.reject(new Error(message));
        });
}

/**
 * Marks the latest run as accepted in the `ai_events` log. A failure here must not disturb the
 * editor, the answer is already in the article, so it is only logged to the console.
 */
function reportApplied(superdesk: ISuperdeskApi, article: IArticleLike, feature: IWidgetFeature, index: number) {
    const eventId = lastRunEventIds.get(runKey(article._id, ACTION_TYPE_OF_FEATURE[feature]));

    if (eventId == null) {
        return;
    }

    superdesk
        .httpRequestJsonLocal({
            method: 'PATCH',
            path: `/ai_events/${eventId}`,
            payload: {outcome: 'accepted', applied_index: index},
        })
        .catch((error) => {
            console.warn('AI assistant: reporting the outcome of a run failed', error);
        });
}

export function configureAiWidget(superdesk: ISuperdeskApi) {
    return {
        onAnswerApplied: (article: IArticleLike, feature: IWidgetFeature, index: number) =>
            reportApplied(superdesk, article, feature, index),

        generateHeadlines: (article: IArticleLike, abortSignal: AbortSignal) =>
            runAction(superdesk, 'suggestion', article, abortSignal),

        generateSummary: (article: IArticleLike, abortSignal: AbortSignal) =>
            runAction(superdesk, 'summary', article, abortSignal).then((texts) => texts[0] ?? ''),
    };
}
