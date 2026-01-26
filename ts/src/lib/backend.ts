import { createProtoClient } from "ankiutils";

import {
    BackendService,
    type GetDefaultFillFieldsResponse,
    type GetLanguagesAndProvidersResponse,
    type GetLanguagesResponse,
    type GetProvidersForLanguageResponse,
    type GetSentencesResponse,
    type GetSettingsResponse,
    type GetSupportLinksResponse,
    type GetTatoebaLanguagesResponse,
    type Provider,
    type ProviderOptions,
    type SaveSettingsRequest,
    type Sentence,
    type TatoebaDownloadProgress,
} from "./generated/backend_pb";

export const client = createProtoClient(BackendService);

export {
    type GetDefaultFillFieldsResponse,
    type GetLanguagesAndProvidersResponse,
    type GetLanguagesResponse,
    type GetProvidersForLanguageResponse,
    type GetSentencesResponse,
    type GetSettingsResponse,
    type GetSupportLinksResponse,
    type GetTatoebaLanguagesResponse,
    type Provider,
    type ProviderOptions,
    type SaveSettingsRequest,
    type Sentence,
    type TatoebaDownloadProgress,
};
