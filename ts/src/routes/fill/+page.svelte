<script lang="ts">
    import {
        client,
        type GetDefaultFillFieldsResponse,
        promiseWithResolver,
        type Provider,
    } from "$lib";
    import Select from "$lib/Select.svelte";
    import Spinner from "$lib/Spinner.svelte";
    import { onMount } from "svelte";

    import type { PageProps } from "./$types";

    let { data }: PageProps = $props();

    let { nids } = data;

    let [initialDataPromise, resolveInitialData] = promiseWithResolver<
        GetDefaultFillFieldsResponse
    >();
    let providers = $state<Provider[]>([]);
    let selectedLanguage = $state<string>("");
    let selectedProvider = $state<string>("");
    let selectedWordField = $state<string>("");
    let selectedSentencesField = $state<string>("");
    let selectedNumberOfSentences = $state<number>(0);

    onMount(() => {
        client.getDefaultFillFields({ nids }).then((response) => {
            resolveInitialData(response);
            providers = response.providers;
            selectedNumberOfSentences = response.numberOfSentences;
            selectedLanguage = response.language;
            selectedProvider = response.provider;
            selectedWordField = response.wordField;
            selectedSentencesField = response.sentencesField;
        });
    });

    async function onLanguageSelected(language: string) {
        console.log("onLanguageSelected", language);
        const response = await client.getProvidersForLanguage({
            language,
        });
        providers = response.providers;
    }

    async function onProcess() {
        await client.fillInSentences({
            language: selectedLanguage,
            provider: selectedProvider,
            wordField: selectedWordField,
            sentencesField: selectedSentencesField,
            numberOfSentences: selectedNumberOfSentences,
            nids: nids,
        });
    }
</script>

<div class="container">
    {#await initialDataPromise}
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
                        clearable={false}
                        bind:value={selectedLanguage}
                        onSelected={onLanguageSelected}
                    />
                </div>
            </div>
            <div class="mb-3 row">
                <label for="provider" class="col-sm-3 col-form-label"
                >Provider</label>
                <div class="col-sm-9">
                    <Select
                        id="provider"
                        options={providers.map(provider => ({
                            value: provider.code,
                            label: provider.name,
                        }))}
                        clearable={false}
                        bind:value={selectedProvider}
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
                        clearable={false}
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
                        clearable={false}
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
    {/await}
</div>

<style lang="scss">
</style>
