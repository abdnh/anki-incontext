<script lang="ts">
    import type { Sentence } from "$lib";
    import {
        client,
        type GetLanguagesAndProvidersResponse,
        promiseWithResolver,
    } from "$lib";
    import { ClipboardMonitor } from "$lib/clipboard-monitor";
    import Error from "$lib/Error.svelte";
    import { type SelectOption } from "$lib/SelectOptions.svelte";
    import Spinner from "$lib/Spinner.svelte";
    import { onMount } from "svelte";
    import type { PageProps } from "./$types";
    import SearchField from "./SearchField.svelte";
    import SearchLanguageSelector from "./SearchLanguageSelector.svelte";
    import SearchProviderDropdown from "./SearchProviderDropdown.svelte";
    import SentenceCard from "./SentenceCard.svelte";

    let { data }: PageProps = $props();

    let [languagesPromise, resolveLanguages, rejectLanguages] =
        promiseWithResolver<
            SelectOption[]
        >();
    let search = $state(data.word);
    let selectedLanguage = $state(data.language);
    let providers = $state<SelectOption[]>([]);
    let selectedProviders = $state<string[]>(data.providers ?? []);
    let sentences = $state<Sentence[] | undefined>([]);
    let loadingSentences = $state(false);
    let clipboardMonitor = new ClipboardMonitor();
    let clipboardMonitorEnabled = $state(false);
    let clipboardIcon = $derived.by(() =>
        clipboardMonitorEnabled ? "clipboard-pulse" : "clipboard"
    );
    let clipboardButtonType = $derived.by(() =>
        clipboardMonitorEnabled ? "btn-success" : "btn-secondary"
    );
    function onSearch() {
        loadingSentences = true;
        client.getSentences({
            word: search,
            language: selectedLanguage,
            providers: selectedProviders,
        }).then((response) => {
            sentences = response.sentences.length
                ? response.sentences
                : undefined;
            loadingSentences = false;
        });
    }

    function onLanguageSelected() {
        client.getProvidersForLanguage({ language: selectedLanguage })
            .then(
                (response) => {
                    providers = response.providers.map(provider => ({
                        value: provider.code,
                        label: provider.name,
                    }));
                    selectedProviders = providers.map(p => p.value);
                },
            );
    }

    function toggleClipboardMonitor() {
        clipboardMonitorEnabled = !clipboardMonitorEnabled;
        if (clipboardMonitorEnabled) {
            clipboardMonitor.start((text) => {
                search = text;
                onSearch();
            });
        } else {
            clipboardMonitor.stop();
        }
    }

    onMount(async () => {
        let response: GetLanguagesAndProvidersResponse;
        try {
            response = await client.getLanguagesAndProviders({
                defaultLanguage: selectedLanguage,
            });
        } catch (error) {
            rejectLanguages(error);
            return;
        }
        const languages = response.languages.map(lang => ({
            value: lang.code,
            label: lang.name,
        }));
        providers = response.defaultProviders.map(provider => ({
            value: provider.code,
            label: provider.name,
        }));
        selectedProviders = data.providers
            ?? response.defaultProviders.map(provider => provider.code);
        resolveLanguages(languages);
    });
</script>

<div class="container search-container">
    {#await languagesPromise}
        <Spinner />
    {:then languages}
        <h1 class="text-center">Search for sentences across the web!</h1>
        <div class="input-container">
            <SearchLanguageSelector
                bind:selectedLanguage={selectedLanguage}
                languages={languages}
                {onLanguageSelected}
            />
            <div class="search-field">
                <SearchField
                    bind:value={search}
                    onSearch={onSearch}
                    autoTrigger={data.autoSearch}
                />
            </div>
            <button
                class="btn {clipboardButtonType}"
                aria-label="Toggle clipboard monitor"
                title="Toggle clipboard monitor"
                onclick={toggleClipboardMonitor}
            >
                <i class="bi bi-{clipboardIcon}"></i>
            </button>
        </div>
        <div class="filters-container">
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
            <div class="sentences">
                {#each sentences as sentence, i (i)}
                    <SentenceCard
                        text={sentence.text}
                        url={sentence.url}
                        provider={sentence.provider}
                        alternativeColor={i % 2 === 0}
                    />
                {/each}
            </div>
        {:else}
            <div class="empty">
                <i class="bi bi-hdd"></i>
                <div>No Results</div>
            </div>
        {/if}
    {:catch error}
        <Error error={error.rawMessage} />
    {/await}
</div>

<style lang="scss">
    .search-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .input-container {
        display: flex;
        gap: 0.5rem;
    }

    .filters-container {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        font-size: 1.5em;
    }
    .search-field {
        flex: 1;
    }
    .sentences {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }
    .empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-inline: auto;
        font-size: 1.5em;
    }
</style>
