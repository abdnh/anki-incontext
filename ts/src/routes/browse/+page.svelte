<script lang="ts">
    import type { Sentence } from "$lib";
    import { client, promiseWithResolver } from "$lib";
    import { type SelectOption } from "$lib/BaseSelect.svelte";
    import MultiSelect from "$lib/MultiSelect.svelte";
    import Select from "$lib/Select.svelte";
    import Spinner from "$lib/Spinner.svelte";
    import { onMount } from "svelte";
    import SearchField from "./SearchField.svelte";
    import SentenceCard from "./SentenceCard.svelte";
    let search = $state("");
    let selectedLanguage = $state("");

    let [languagesPromise, resolveLanguages] = promiseWithResolver<
        Array<{ value: string; label: string }>
    >();
    let providers = $state<SelectOption[]>([]);
    let selectedProviders = $state<string[]>([]);
    let sentences = $state<Sentence[]>([]);
    let loadingSentences = $state(false);

    onMount(() => {
        client.getLanguages({}).then((response) => {
            resolveLanguages(response.languages.map(lang => ({
                value: lang.code,
                label: lang.name,
            })));
        });
    });

    function onSearch() {
        loadingSentences = true;
        client.getSentences({
            word: search,
            language: selectedLanguage,
            providers: selectedProviders,
        }).then((response) => {
            sentences = response.sentences;
            loadingSentences = false;
        });
    }

    function onLanguageSelected(language: string) {
        client.getProvidersForLanguage({ language }).then(
            (response) => {
                providers = response.providers.map(provider => ({
                    value: provider.code,
                    label: provider.name,
                }));
                selectedProviders = providers.map(provider =>
                    provider.value
                );
            },
        );
    }
</script>

<div class="container search-container">
    {#await languagesPromise}
        <Spinner />
    {:then languages}
        <h1>Browse sentences</h1>
        <Select
            options={languages}
            bind:value={selectedLanguage}
            placeholder="Select a language..."
            searchPlaceholder="Search languages..."
            onSelected={onLanguageSelected}
        />
        <MultiSelect
            options={providers}
            bind:selectedOptions={selectedProviders}
            placeholder="Select a provider..."
            searchPlaceholder="Search providers..."
        />
        <SearchField bind:value={search} onSearch={onSearch} />
        {#if loadingSentences}
            <Spinner label="Loading sentences..." />
        {:else}
            <div class="sentences">
                {#each sentences as sentence, i}
                    <SentenceCard
                        text={sentence.text}
                        url={sentence.url}
                        alternativeColor={i % 2 === 0}
                    />
                {/each}
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

    .sentences {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }
</style>
