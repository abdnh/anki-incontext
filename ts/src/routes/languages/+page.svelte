<script lang="ts">
    import {
        client,
        type GetLanguagesAndProvidersResponse,
        type Provider,
    } from "$lib";
    import Error from "$lib/Error.svelte";
    import LanguageSelect from "$lib/LanguageSelect.svelte";
    import SelectControl from "$lib/SelectControl.svelte";
    import { promiseWithResolver, type SelectOption, Spinner } from "ankiutils";
    import { onMount } from "svelte";

    let [languagesPromise, resolveLanguages, _] = promiseWithResolver<
        GetLanguagesAndProvidersResponse
    >();
    let language = $state("eng");
    let languages = $state<SelectOption[]>([]);
    let providers = $state<Provider[]>([]);

    async function onLanguageSelected(lang: string) {
        console.log("onLanguageSelected", lang, language);
        const response = await client.getProvidersForLanguage({
            language: lang,
        });
        providers = response.providers;
    }

    onMount(async () => {
        const response = await client.getLanguagesAndProviders({
            defaultLanguage: language,
        });
        resolveLanguages(response);
        languages = response.languages.map(lang => {
            return { label: lang.name, value: lang.code };
        });
        providers = response.providers;
    });
</script>

<div class="container mx-auto min-h-screen flex flex-col gap-4 p-4">
    <h2 class="font-bold text-4xl my-4">Supported Languages and Providers</h2>

    <p>
        This page lists all languages supported by InContext, along with the
        providers available for each language. The codes are useful if you're
        using the add-on's custom template filter.
    </p>

    {#await languagesPromise}
        <Spinner label="Loading languages..." />
    {:then _}
        <SelectControl label="Language">
            <LanguageSelect
                options={languages}
                onSelected={onLanguageSelected}
                bind:value={language}
            />
        </SelectControl>
        <p>Language code: {language}</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each providers as provider (provider.code)}
                <div class="card bg-base-100 shadow-sm">
                    <div class="card-body">
                        <h2 class="card-title">{provider.name}</h2>
                        <p>
                            code: {provider.code}
                        </p>
                        <div class="card-actions justify-end">
                            <a
                                class="btn btn-primary"
                                href={provider.url}
                                target="_blank"
                                aria-label="Visit website"
                            >Visit</a>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:catch error}
        <Error error={error.rawMessage} />
    {/await}
</div>

<style lang="scss">
    :global(html) {
        font-size: 20px;
    }
</style>
