<script lang="ts">
    import {
        client,
        type GetSettingsResponse,
        promiseWithResolver,
    } from "$lib";
    import Error from "$lib/Error.svelte";
    import MultiSelect from "$lib/MultiSelect.svelte";
    import Select from "$lib/Select.svelte";
    import type { SelectOption } from "$lib/SelectOptions.svelte";
    import Spinner from "$lib/Spinner.svelte";
    import { onMount } from "svelte";
    import SearchShortcut from "./SearchShortcut.svelte";

    interface Shortcut {
        keys: string[];
        language: string;
        providers: string[];
    }

    let searchShortcuts = $state<Shortcut[]>([]);
    let [settingsPromise, resolveSettings, rejectSettings] =
        promiseWithResolver<
            GetSettingsResponse
        >();
    let providersForLanguage: {
        [key: string]: Promise<SelectOption[]>;
    } = $state({});

    function onAddSearchShortcut() {
        searchShortcuts.push({ keys: [], language: "", providers: [] });
    }

    function onSave() {
        client.saveSettings({
            searchShortcuts: searchShortcuts.map(shortcut => {
                return {
                    keys: shortcut.keys,
                    language: shortcut.language,
                    selectedProviders: shortcut.providers,
                };
            }),
        });
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
        searchShortcuts = response.searchShortcuts.map(s => {
            providersForLanguage[s.language] = new Promise(
                (resolve, _) => {
                    resolve(s.providers.map(p => {
                        return { label: p.name, value: p.code };
                    }));
                },
            );
            return {
                keys: s.keys,
                language: s.language,
                providers: s.selectedProviders,
            };
        });
    });
</script>

<div class="container page">
    {#await settingsPromise}
        <Spinner />
    {:then settings}
        <div class="search-shortcuts">
            <div class="search-shortcuts-header">
                <h2>Search Shortcuts</h2>
                <button
                    class="btn btn-primary"
                    aria-label="Add search shortcut"
                    onclick={onAddSearchShortcut}
                >
                    <i class="bi bi-plus"></i>
                </button>
            </div>
            <div class="search-shortcuts-container">
                <p>
                    Assign shortcuts to search for sentences for the selected
                    word in any language
                </p>
                {#each searchShortcuts as _, i}
                    <div class="search-shortcut-widget">
                        <SearchShortcut bind:keys={searchShortcuts[i].keys} />
                        <Select
                            options={settings.languages.map(lang => {
                                return {
                                    label: lang.name,
                                    value: lang.code,
                                };
                            })}
                            bind:value={searchShortcuts[i].language}
                            placeholder="Select language"
                            onSelected={(lang) => {
                                if (!providersForLanguage[lang]) {
                                    providersForLanguage[lang] =
                                        client
                                            .getProvidersForLanguage({
                                                language: lang,
                                            })
                                            .then(response => {
                                                const providers =
                                                    response.providers
                                                        .map(p => {
                                                            return {
                                                                label:
                                                                    p.name,
                                                                value:
                                                                    p.code,
                                                            };
                                                        });
                                                searchShortcuts[i]
                                                    .providers =
                                                        providers.map(
                                                            p => p
                                                                .value,
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
                                options={providers}
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
        </div>
        <div class="action-buttons">
            <button class="btn btn-primary" onclick={onSave}>Save</button>
        </div>
    {:catch error}
        <Error error={error.rawMessage} />
    {/await}
</div>

<style lang="scss">
    :global(body) {
        height: 100vh;
    }
    .page {
        display: flex;
        flex-direction: column;
        gap: 16px;
        height: 100%;
    }
    .search-shortcuts {
        flex: 1;
    }
    .search-shortcuts-header {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }
    .search-shortcuts-container {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    .search-shortcut-widget {
        display: flex;
        flex-direction: row;
        gap: 16px;
    }
    .search-shortcut-widget > :global(:not(button)) {
        flex: 1;
    }
    .action-buttons {
        display: flex;
        flex-direction: row-reverse;
        border-top: 1px solid rgb(161, 156, 156);
        padding-top: 8px;
    }
</style>
