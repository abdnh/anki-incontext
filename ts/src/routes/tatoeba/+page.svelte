<script lang="ts">
    import { client, type TatoebaDownloadProgress } from "$lib";
    import Error from "$lib/Error.svelte";
    import Select from "$lib/Select.svelte";
    import Spinner from "$lib/Spinner.svelte";

    let selectedLanguage = $state("");
    let downloadProgress = $state<TatoebaDownloadProgress | null>(null);

    async function getLanguages() {
        const response = await client.getTatoebaLanguages({});
        return response.languages.map(lang => ({
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

<div class="container">
    {#await getLanguages()}
        <Spinner label="Fetching languages..." />
    {:then languages}
        <div class="mt-4">
            <p>Select a language to download sentences from Tatoeba.</p>
            <Select
                options={languages}
                bind:value={selectedLanguage}
                placeholder="Select a language..."
                searchPlaceholder="Search languages..."
            />
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
    {:catch error}
        <Error error={error.rawMessage} />
    {/await}
</div>
