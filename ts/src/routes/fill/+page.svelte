<script lang="ts">
    import { client, type Provider } from "$lib";
    import { MultiSelect, Select, Spinner } from "ankiutils";

    import Error from "$lib/Error.svelte";
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
            : response.languageProviders.map((provider) =>
                provider.code
            );
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
            <label class="form-control">
                <span class="label">Language</span>
                <div class="input-container">
                    <Select
                        options={initialData.languages.map((lang) => ({
                            value: lang.code,
                            label: lang.name,
                        }))}
                        bind:value={selectedLanguage}
                        onSelected={onLanguageSelected}
                    />
                </div>
            </label>

            <label class="form-control">
                <span class="label">Providers</span>
                <div class="input-container">
                    <MultiSelect
                        options={providers.map((provider) => ({
                            value: provider.code,
                            label: provider.name,
                        }))}
                        bind:selectedOptions={selectedProviders}
                    />
                </div>
            </label>
            <label class="form-control">
                <span class="label">Word field</span>
                <div class="input-container">
                    <Select
                        options={initialData.fields.map((field) => ({
                            value: field,
                            label: field,
                        }))}
                        bind:value={selectedWordField}
                    />
                </div>
            </label>
            <label class="form-control">
                <span class="label">Sentences field</span>
                <div class="input-container">
                    <Select
                        options={initialData.fields.map((field) => ({
                            value: field,
                            label: field,
                        }))}
                        bind:value={selectedSentencesField}
                    />
                </div>
            </label>
            <label class="form-control">
                <span class="label">Number of sentences</span>
                <input
                    type="number"
                    class="input"
                    bind:value={selectedNumberOfSentences}
                />
            </label>
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

    .form-control {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;

        .label {
            grid-column: span 1 / span 1;
        }
        .input-container,
        input {
            grid-column: span 3 / span 3;
            width: 100%;
        }
        .input-container {
            & > :global(*) {
                width: 100%;
            }

            :global(input) {
                flex-grow: 1;
            }
        }
    }
</style>
