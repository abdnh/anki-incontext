<script lang="ts">
    import { client, type Provider } from "$lib";
    import { MultiSelect, Select, Spinner } from "ankiutils";

    import Error from "$lib/Error.svelte";
    import SelectControl from "$lib/SelectControl.svelte";
    import type { PageProps } from "./$types";

    let { data }: PageProps = $props();

    let nids = data.nids.map((nid) => BigInt(nid));

    let providers = $state<Provider[]>([]);
    let selectedLanguage = $state<string>("");
    let selectedProviders = $state<string[]>([]);
    let selectedWordField = $state<string>("");
    let selectedSentencesField = $state<string>("");
    let selectedNumberOfSentences = $state<bigint>(0n);

    async function getInitialData() {
        const response = await client.getDefaultFillFields({
            nids,
        });
        providers = response.languageProviders;
        selectedNumberOfSentences = response.numberOfSentences;
        selectedLanguage = response.language;
        selectedProviders = response.providers.length > 0
            ? response.providers
            : response.languageProviders.map((provider) => provider.code);
        selectedWordField = response.wordField;
        selectedSentencesField = response.sentencesField;
        return response;
    }

    async function onLanguageSelected(language: string) {
        const response = await client.getProvidersForLanguage({
            language,
        });
        providers = response.providers;
        selectedProviders = selectedProviders.filter((provider) =>
            response.providers.some((p) => p.code === provider)
        );
    }

    async function onProcess() {
        await client.fillInSentences({
            language: selectedLanguage,
            providers: selectedProviders,
            wordField: selectedWordField,
            sentencesField: selectedSentencesField,
            numberOfSentences: selectedNumberOfSentences,
            nids: nids,
        });
    }
</script>

<div class="container mx-auto min-h-screen p-4">
    {#await getInitialData()}
        <Spinner />
    {:then initialData}
        <h1 class="font-bold text-2xl my-2">Fill in sentences</h1>
        <div class="flex flex-col gap-2">
            <SelectControl label="Language">
                <Select
                    options={initialData.languages.map((lang) => ({
                        value: lang.code,
                        label: lang.name,
                    }))}
                    bind:value={selectedLanguage}
                    onSelected={onLanguageSelected}
                />
            </SelectControl>
            <SelectControl label="Providers">
                <MultiSelect
                    options={providers.map((provider) => ({
                        value: provider.code,
                        label: provider.name,
                    }))}
                    bind:selectedOptions={selectedProviders}
                />
            </SelectControl>
            <SelectControl label="Word field">
                <Select
                    options={initialData.fields.map((field) => ({
                        value: field,
                        label: field,
                    }))}
                    bind:value={selectedWordField}
                />
            </SelectControl>
            <SelectControl label="Sentences field"><Select
                    options={initialData.fields.map((field) => ({
                        value: field,
                        label: field,
                    }))}
                    bind:value={selectedSentencesField}
                /></SelectControl>
            <SelectControl label="Number of sentences">
                <input
                    type="number"
                    class="input"
                    bind:value={selectedNumberOfSentences}
                />
            </SelectControl>
            <button
                type="button"
                class="btn btn-primary self-end"
                onclick={onProcess}
            >
                Process
            </button>
        </div>
    {:catch error}
        <Error error={error.rawMessage} />
    {/await}
</div>

<style lang="scss">
    :global(html) {
        font-size: 24px;
    }
</style>
