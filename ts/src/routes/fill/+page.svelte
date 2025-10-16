<script lang="ts">
    import { client, type Provider } from "$lib";
    import Select from "$lib/Select.svelte";
    import Spinner from "$lib/Spinner.svelte";

    import Error from "$lib/Error.svelte";
    import MultiSelect from "$lib/MultiSelect.svelte";
    import type { PageProps } from "./$types";

    let { data }: PageProps = $props();

    let nids = data.nids.map(nid => BigInt(nid));

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
            : response.languageProviders.map(provider => provider.code);
        selectedWordField = response.wordField;
        selectedSentencesField = response.sentencesField;
        return response;
    }

    async function onLanguageSelected(language: string) {
        const response = await client.getProvidersForLanguage({
            language,
        });
        providers = response.providers;
        selectedProviders = selectedProviders.filter(provider =>
            response.providers.some(p => p.code === provider)
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

<div class="container">
    {#await getInitialData()}
        <Spinner />
    {:then initialData}
        <h1>Fill in sentences</h1>
        <form>
            <div class="mb-3 row">
                <label for="language" class="col-sm-3 col-form-label"
                >Language</label>
                <div class="col-sm-9">
                    <Select
                        id="language"
                        options={initialData.languages.map(lang => ({
                            value: lang.code,
                            label: lang.name,
                        }))}
                        bind:value={selectedLanguage}
                        onSelected={onLanguageSelected}
                    />
                </div>
            </div>
            <div class="mb-3 row">
                <label for="provider" class="col-sm-3 col-form-label"
                >Providers</label>
                <div class="col-sm-9">
                    <MultiSelect
                        id="provider"
                        options={providers.map(provider => ({
                            value: provider.code,
                            label: provider.name,
                        }))}
                        bind:selectedOptions={selectedProviders}
                    />
                </div>
            </div>
            <div class="mb-3 row">
                <label for="word" class="col-sm-3 col-form-label"
                >Word field</label>
                <div class="col-sm-9">
                    <Select
                        id="word"
                        options={initialData.fields.map(field => ({
                            value: field,
                            label: field,
                        }))}
                        bind:value={selectedWordField}
                    />
                </div>
            </div>
            <div class="mb-3 row">
                <label for="sentences" class="col-sm-3 col-form-label"
                >Sentences field</label>
                <div class="col-sm-9">
                    <Select
                        id="sentences"
                        options={initialData.fields.map(field => ({
                            value: field,
                            label: field,
                        }))}
                        bind:value={selectedSentencesField}
                    />
                </div>
            </div>
            <div class="mb-3 row">
                <label for="number" class="col-sm-3 col-form-label"
                >Number of sentences</label>
                <div class="col-sm-9">
                    <input
                        type="number"
                        id="number"
                        class="form-control"
                        bind:value={selectedNumberOfSentences}
                    />
                </div>
            </div>
            <div class="mb-3 row">
                <div class="col-sm-9 offset-sm-2">
                    <button
                        type="button"
                        class="btn btn-primary"
                        onclick={onProcess}
                    >
                        Process
                    </button>
                </div>
            </div>
        </form>
    {:catch error}
        <Error error={error.rawMessage} />
    {/await}
</div>

<style lang="scss">
</style>
