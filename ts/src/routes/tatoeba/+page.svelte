<script lang="ts">
    import {
        client,
        type GetTatoebaLanguagesResponse,
        promiseWithResolver,
        type TatoebaDownloadProgress,
    } from "$lib";
    import Spinner from "$lib/Spinner.svelte";

    import { onMount } from "svelte";

    let [languagesPromise, resolveLanguages] = promiseWithResolver<
        GetTatoebaLanguagesResponse
    >();

    let selectedLanguage = $state("");
    let downloadProgress = $state<TatoebaDownloadProgress | null>(null);

    onMount(() => {
        client.getTatoebaLanguages({}).then(resolveLanguages);
    });

    async function onDownload() {
        if (!selectedLanguage) {
            return;
        }
        await client.downloadTatoebaSentences({
            language: selectedLanguage,
        });
        const intervalId = setInterval(() => {
            client.getTatoebaDownloadProgress({}).then((progress) => {
                downloadProgress = progress;
                if (progress.isError || progress.finished) {
                    clearInterval(intervalId);
                }
            });
        }, 1000);
    }
</script>

<div class="container">
    {#await languagesPromise}
        <Spinner label="Fetching languages..." />
    {:then languages}
        <div class="mt-4">
            <h2 class="mb-3">Select a language</h2>
            <select class="form-select" bind:value={selectedLanguage}>
                {#each languages.languages as language}
                    <option value={language.code}>{language.name}</option>
                {/each}
            </select>
            <button class="btn btn-primary mt-3" onclick={onDownload}>
                Download
            </button>
            {#if downloadProgress}
                {#if !downloadProgress.finished}
                    <div
                        class="progress mt-3"
                        role="progressbar"
                        aria-label="Tatoeba download progress"
                        aria-valuenow={downloadProgress.progress}
                        aria-valuemin="0"
                        aria-valuemax="100"
                    >
                        <div
                            class={`progress-bar progress-bar-striped ${
                                downloadProgress.finished
                                    ? ""
                                    : "progress-bar-animated"
                            }`}
                            style={`width: ${downloadProgress.progress * 100}%`}
                        >
                        </div>
                    </div>
                {/if}
                <div
                    class={`alert alert-${
                        downloadProgress.isError ? "danger" : "info"
                    } mt-3`}
                >
                    {downloadProgress.message}
                </div>
            {/if}
        </div>
    {/await}
</div>

<style>
</style>
