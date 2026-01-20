<script lang="ts">
    import type { Sentence } from "$lib";
    import { client, type GetLanguagesAndProvidersResponse } from "$lib";
    import Error from "$lib/Error.svelte";
    import type { ConnectError } from "@connectrpc/connect";
    import { promiseWithResolver, type SelectOption, Spinner } from "ankiutils";
    import { onMount } from "svelte";
    import type { PageProps } from "./$types";
    import SearchField from "./SearchField.svelte";
    import SearchLanguageSelector from "./SearchLanguageSelector.svelte";
    import SearchProviderDropdown from "./SearchProviderDropdown.svelte";
    import SentenceCard from "./SentenceCard.svelte";

    let { data }: PageProps = $props();

    let [languagesPromise, resolveLanguages, rejectLanguages] =
        promiseWithResolver<SelectOption[]>();
    let search = $state(data.word);
    let initialLanguage = data.language ?? undefined;
    let selectedLanguage = $state(initialLanguage ?? "eng");
    let providers = $state<SelectOption[]>([]);
    let selectedProviders = $state<string[]>(data.providers ?? []);
    let sentences = $state<Sentence[] | null>([]);
    let loadingSentences = $state(false);
    let searchError = $state<string | null>(null);
    let ignoreNextClipboardUpdate = $state(false);
    let abortController: AbortController | null = $state(null);

    async function runQuery(query: {
        word: string;
        language: string;
        providers: string[];
    }) {
        search = query.word;
        const oldLanguage = selectedLanguage;
        selectedLanguage = query.language;
        if (query.language != oldLanguage) {
            await onLanguageSelected();
            selectedProviders = query.providers;
        } else {
            selectedProviders = query.providers;
        }
        onSearch();
    }

    window.incontext = window.incontext || {};
    window.incontext.runQuery = runQuery;

    async function onSearch() {
        if (abortController) {
            abortController.abort();
        }
        loadingSentences = true;
        abortController = new AbortController();
        try {
            const response = await client
                .getSentences(
                    {
                        word: search,
                        language: selectedLanguage,
                        providers: selectedProviders,
                    },
                    { signal: abortController.signal },
                );

            sentences = response.sentences.length
                ? response.sentences
                : null;

            searchError = null;
        } catch (error) {
            searchError = (error as ConnectError).rawMessage;
            sentences = null;
        }
        loadingSentences = false;
    }

    async function onLanguageSelected() {
        const response = await client.getProvidersForLanguage({
            language: selectedLanguage,
        });
        providers = response.providers.map((provider) => ({
            value: provider.code,
            label: provider.name,
        }));
        selectedProviders = providers.map((p) => p.value);
    }

    function onCopy(_event: ClipboardEvent) {
        ignoreNextClipboardUpdate = true;
    }

    onMount(async () => {
        let response: GetLanguagesAndProvidersResponse;
        try {
            response = await client.getLanguagesAndProviders({
                defaultLanguage: initialLanguage,
            });
        } catch (error) {
            rejectLanguages(error);
            return;
        }
        selectedLanguage = response.defaultLanguage;
        const languages = response.languages.map((lang) => ({
            value: lang.code,
            label: lang.name,
        }));
        providers = response.providers.map((provider) => ({
            value: provider.code,
            label: provider.name,
        }));
        selectedProviders = data.providers ?? response.defaultProviders;
        resolveLanguages(languages);
    });
</script>

<svelte:window oncopy={onCopy} />

<div class="container mx-auto min-h-screen flex-col gap-2 p-2">
    {#await languagesPromise}
        <Spinner />
    {:then languages}
        <h1 class="text-center font-bold text-4xl my-2">
            Search for sentences across the web
        </h1>
        <div class="flex gap-2 items-center mb-2">
            <SearchLanguageSelector
                bind:selectedLanguage
                {languages}
                {onLanguageSelected}
            />
            <div class="flex-1">
                <SearchField
                    bind:value={search}
                    bind:ignoreNextClipboardUpdate
                    {onSearch}
                    autoTrigger={data.autoSearch}
                />
            </div>
        </div>
        <div class="flex justify-start items-center text-2xl gap-2">
            <i class="bi bi-filter"></i>
            <SearchProviderDropdown
                label="Providers"
                options={providers}
                bind:selectedOptions={selectedProviders}
            />
        </div>
        {#if loadingSentences}
            <Spinner label="Loading sentences..." />
        {:else if sentences}
            <div class="flex flex-col gap-4 mt-4">
                {#each sentences as sentence, i (i)}
                    <SentenceCard
                        text={sentence.text}
                        url={sentence.source}
                        provider={sentence.provider}
                        alternativeColor={i % 2 === 0}
                    />
                {/each}
            </div>
        {:else if searchError}
            <Error error={searchError} />
        {:else}
            <div class="flex flex-col items-center mx-auto text-2xl">
                <i class="bi bi-hdd"></i>
                <div>No Results</div>
            </div>
        {/if}
    {:catch error}
        <Error error={error.rawMessage} />
    {/await}
</div>
