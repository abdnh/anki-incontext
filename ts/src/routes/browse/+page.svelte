<script lang="ts">
    import type { Sentence } from "$lib";
    import { client, promiseWithResolver } from "$lib";
    import { type SelectOption } from "$lib/SelectOptions.svelte";
    import Spinner from "$lib/Spinner.svelte";
    import { onMount } from "svelte";
    import SearchField from "./SearchField.svelte";
    import SearchLanguageSelector from "./SearchLanguageSelector.svelte";
    import SearchProviderDropdown from "./SearchProviderDropdown.svelte";
    import SentenceCard from "./SentenceCard.svelte";

    let search = $state("");
    let selectedLanguage = $state("");
    let [languagesPromise, resolveLanguages] = promiseWithResolver<
        SelectOption[]
    >();
    let providers = $state<SelectOption[]>([]);
    let selectedProviders = $state<string[]>([]);
    let sentences = $state<Sentence[] | undefined>([]);
    let loadingSentences = $state(false);

    onMount(() => {
        client.getDefaultFillFields({}).then((response) => {
            resolveLanguages(response.languages.map(lang => ({
                value: lang.code,
                label: lang.name,
            })));
            selectedLanguage = response.language;
            providers = response.languageProviders.map(provider => ({
                value: provider.code,
                label: provider.name,
            }));
            selectedProviders = response.providers.length > 0
                ? response.providers
                : response.languageProviders.map(provider =>
                    provider.code
                );
        });
    });

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
                    selectedProviders = selectedProviders.filter(
                        provider =>
                            response.providers.some(p =>
                                p.code === provider
                            ),
                    );
                },
            );
    }
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
                />
            </div>
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
                {#each sentences as sentence, i}
                    <SentenceCard
                        text={sentence.text}
                        url={sentence.url}
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
