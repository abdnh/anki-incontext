<script lang="ts">
    import { client, type GetSettingsResponse } from "$lib";
    import Error from "$lib/Error.svelte";
    import SelectControl from "$lib/SelectControl.svelte";
    import {
        MultiSelect,
        promiseWithResolver,
        Select,
        type SelectOption,
        Spinner,
    } from "ankiutils";
    import { type Component, onMount } from "svelte";
    import Nadeshiko from "./Nadeshiko.svelte";
    import SearchShortcut from "./SearchShortcut.svelte";
    import type { ProviderOptions } from "./types";

    interface Shortcut {
        keys: string[];
        language: string;
        providers: string[];
    }
    let languages = $state<SelectOption[]>([]);
    let providers = $state<SelectOption[]>([]);
    let defaultLanguage = $state("");
    let defaultProviders = $state<string[]>([]);
    let searchShortcuts = $state<Shortcut[]>([]);
    let [settingsPromise, resolveSettings, rejectSettings] =
        promiseWithResolver<GetSettingsResponse>();
    let providersForLanguage: {
        [key: string]: Promise<SelectOption[] | undefined>;
    } = $state({});
    let providerOptions = $state<ProviderOptions[]>([]);
    let configuredProvider = $state("");
    let providerOptionComponents: Record<
        string,
        Component
    > = {
        "nadeshiko": Nadeshiko,
    };
    let ConfiguredProviderOptions = $derived(
        providerOptionComponents[configuredProvider],
    );

    function onAddSearchShortcut() {
        searchShortcuts.push({ keys: [], language: "", providers: [] });
    }

    function onSave() {
        client.saveSettings({
            searchShortcuts: searchShortcuts.map((shortcut) => {
                return {
                    keys: shortcut.keys,
                    language: shortcut.language,
                    selectedProviders: shortcut.providers,
                };
            }),
            defaultLanguage,
            defaultProviders,
            providerOptions: providerOptions.map(item => {
                return {
                    provider: item.provider,
                    options: JSON.stringify(item.options),
                };
            }),
        });
    }

    async function onLanguageSelected(language: string) {
        const response = await client.getProvidersForLanguage({
            language,
        });
        providers = response.providers.map((provider) => {
            return {
                label: provider.name,
                value: provider.code,
            };
        });
        defaultProviders = defaultProviders.filter((provider) =>
            response.providers.some((p) => p.code === provider)
        );
    }

    onMount(async () => {
        let response: GetSettingsResponse;
        try {
            response = await client.getSettings({});
        } catch (error) {
            rejectSettings(error);
            return;
        }
        resolveSettings(response);
        languages = response.languages.map((lang) => {
            return {
                label: lang.name,
                value: lang.code,
            };
        });
        providers = response.languageProviders.map((provider) => {
            return {
                label: provider.name,
                value: provider.code,
            };
        });
        defaultLanguage = response.defaultLanguage;
        defaultProviders = response.defaultProviders;
        searchShortcuts = response.searchShortcuts.map((s) => {
            providersForLanguage[s.language] = new Promise(
                (resolve, _) => {
                    resolve(
                        s.providers.map((p) => {
                            return { label: p.name, value: p.code };
                        }),
                    );
                },
            );
            return {
                keys: s.keys,
                language: s.language,
                providers: s.selectedProviders,
            };
        });
        providerOptions = response.providerOptions.map(item => {
            return {
                provider: item.provider!,
                options: JSON.parse(item.options),
            };
        });
    });
</script>

<div class="container mx-auto min-h-screen flex flex-col gap-4 p-4">
    {#await settingsPromise}
        <Spinner />
    {:then}
        <div class="flex-1">
            <div class="flex flex-col gap-4">
                <h2 class="font-bold text-4xl my-4">Defaults</h2>
                <p>
                    These options control the defaults used for the Browse and
                    the Fill-in pages
                </p>
                <SelectControl label="Language">
                    <Select
                        onSelected={onLanguageSelected}
                        options={languages}
                        bind:value={defaultLanguage}
                    />
                </SelectControl>
                <SelectControl label="Providers">
                    <MultiSelect
                        options={providers}
                        bind:selectedOptions={defaultProviders}
                    ></MultiSelect>
                </SelectControl>
            </div>
            <div class="flex flex-row justify-between items-center">
                <h2 class="font-bold text-4xl my-4">Search Shortcuts</h2>
                <button
                    class="btn btn-primary"
                    aria-label="Add search shortcut"
                    onclick={onAddSearchShortcut}
                >
                    <i class="bi bi-plus"></i>
                </button>
            </div>
            <div class="flex flex-col gap-4">
                <p>
                    Assign shortcuts to search for sentences for the selected
                    word in any language
                </p>
                {#each searchShortcuts as _, i (i)}
                    <div class="search-shortcut-widget flex gap-4">
                        <SearchShortcut bind:keys={searchShortcuts[i].keys} />
                        <Select
                            options={languages}
                            bind:value={searchShortcuts[i].language}
                            placeholder="Select language"
                            onSelected={(lang) => {
                                if (!providersForLanguage[lang]) {
                                    providersForLanguage[lang] = client
                                        .getProvidersForLanguage({
                                            language: lang,
                                        })
                                        .then((response) => {
                                            const providers = response.providers
                                                .map((p) => {
                                                    return {
                                                        label: p.name,
                                                        value: p.code,
                                                    };
                                                });
                                            searchShortcuts[i]
                                                .providers = providers.map(
                                                    (p) => p.value,
                                                );
                                            return providers;
                                        });
                                }
                            }}
                        />
                        {#await providersForLanguage[
    searchShortcuts[i].language
]
                        }
                            ...
                        {:then providers}
                            <MultiSelect
                                options={providers ? providers : []}
                                bind:selectedOptions={searchShortcuts[i].providers}
                                placeholder="Select providers"
                            />
                        {/await}
                        <button
                            class="btn btn-danger"
                            aria-label="Delete"
                            onclick={() => {
                                searchShortcuts.splice(i, 1);
                            }}
                        >
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                {/each}
            </div>
            <div class="flex flex-col gap-4">
                <h2 class="font-bold text-4xl my-4">Provider Settings</h2>
                <p>
                    Some providers require configuration to work (e.g. API keys)
                </p>
                <SelectControl label="Provider">
                    <Select
                        options={providerOptions.filter(item =>
                            Object.keys(providerOptionComponents).includes(item.provider!.code)
                        ).map(item => {
                            return { label: item.provider!.name, value: item.provider!.code };
                        })}
                        bind:value={configuredProvider}
                    />
                </SelectControl>
                <ConfiguredProviderOptions bind:allOptions={providerOptions} />
            </div>
        </div>
        <div class="flex flex-row-reverse border-t border-t-accent pt-2">
            <button class="btn btn-primary" onclick={onSave}>Save</button>
        </div>
    {:catch error}
        <Error error={error.rawMessage} />
    {/await}
</div>

<style lang="scss">
    :global(html) {
        font-size: 20px;
    }
    .search-shortcut-widget > :global(:not(button)) {
        flex: 1;
    }
</style>
