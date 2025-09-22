import { createClient } from "@connectrpc/connect";
import { createConnectTransport } from "@connectrpc/connect-web";

import {
    BackendService,
    type GetDefaultFillFieldsResponse,
    type GetLanguagesResponse,
    type GetProvidersForLanguageResponse,
    type GetSentencesResponse,
    type GetTatoebaLanguagesResponse,
    type Provider,
    type Sentence,
    type TatoebaDownloadProgress,
} from "./generated/backend_pb";

const transport = createConnectTransport({
    baseUrl: "/api",
    useBinaryFormat: true,
    fetch: (input, init) => {
        const headers = init?.headers ?? {};
        return fetch(input, {
            ...init,
            headers: {
                ...headers,
                "qt-widget-id": window.qtWidgetId,
            },
        });
    },
});

export const client = createClient(BackendService, transport);

export {
    type GetDefaultFillFieldsResponse,
    type GetLanguagesResponse,
    type GetProvidersForLanguageResponse,
    type GetSentencesResponse,
    type GetTatoebaLanguagesResponse,
    type Provider,
    type Sentence,
    type TatoebaDownloadProgress,
};
