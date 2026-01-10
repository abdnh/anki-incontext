<script lang="ts">
    import { client, type GetSettingsResponse } from "$lib";
    import Error from "$lib/Error.svelte";
    import Spinner from "$lib/Spinner.svelte";
    import type { SelectOption } from "ankiutils";
    import {
        MultiSelect,
        promiseWithResolver,
        Select,
    } from "ankiutils";
    import { onMount } from "svelte";
    import SearchShortcut from "./SearchShortcut.svelte";

    interface Shortcut {
        keys: string[];
        language: string;
        providers: string[];
    }

    let searchShortcuts = $state<Shortcut[]>([]);
    let [settingsPromise, resolveSettings, rejectSettings] =
        promiseWithResolver<GetSettingsResponse>();
    let providersForLanguage: {
        [key: string]: Promise<SelectOption[] | undefined>;
    } = $state({});

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
    });
</script>

<div class="container mx-auto min-h-screen flex flex-col gap-4 p-4">
    {#await settingsPromise}
        <Spinner />
    {:then settings}
        <div class="flex-1">
            <div class="flex flex-row justify-between">
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
                {#each searchShortcuts as _, i}
                    <div class="search-shortcut-widget flex gap-4">
                        <SearchShortcut bind:keys={searchShortcuts[i].keys} />
                        <Select
                            options={settings.languages.map((lang) => {
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
                                            .then((response) => {
                                                const providers =
                                                    response.providers
                                                        .map((p) => {
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
                                                            (p) =>
                                                                p.value,
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
