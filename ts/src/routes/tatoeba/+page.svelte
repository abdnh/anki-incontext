<script lang="ts">
    import { client, type TatoebaDownloadProgress } from "$lib";
    import Error from "$lib/Error.svelte";
    import { Select, Spinner } from "ankiutils";

    let selectedLanguage = $state("");
    let downloadProgress = $state<TatoebaDownloadProgress | null>(null);
    let statusClass = $derived.by(() => {
        if (downloadProgress?.isError) return "alert-error";
        if (downloadProgress?.finished) return "alert-success";
        return "alert-info";
    });

    async function getLanguages() {
        const response = await client.getTatoebaLanguages({});
        return response.languages.map((lang) => ({
            value: lang.code,
            label: lang.name,
        }));
    }

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

<div class="container mx-auto min-h-screen p-4">
    {#await getLanguages()}
        <Spinner label="Fetching languages..." />
    {:then languages}
        <div class="mt-4">
            <p class="text-center text-xl">
                Select a language to download sentences from Tatoeba.
            </p>
            <div class="flex items-center gap-2 mt-4 justify-center">
                <Select
                    options={languages}
                    bind:value={selectedLanguage}
                    placeholder="Select a language..."
                    searchPlaceholder="Search languages..."
                />
                <button class="btn btn-primary" onclick={onDownload}>
                    Download
                </button>
            </div>
            {#if downloadProgress}
                {#if !downloadProgress.finished}
                    <progress
                        class="progress progress-primary mt-4"
                        aria-label="Tatoeba download progress"
                        value={downloadProgress.progress}
                        max="100"
                    >
                    </progress>
                {/if}
                <div class={`alert ${statusClass} mt-4`}>
                    {downloadProgress.message}
                </div>
            {/if}
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
