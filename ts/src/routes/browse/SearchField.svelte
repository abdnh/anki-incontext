<script lang="ts">
    import { ClipboardMonitor } from "$lib/clipboard-monitor";
    import { onMount } from "svelte";
    let inputElement: HTMLInputElement;

    interface Props {
        onSearch: () => void;
        value: string;
        autoTrigger: boolean;
        ignoreNextClipboardUpdate: boolean;
    }

    let {
        onSearch,
        value = $bindable(""),
        autoTrigger = false,
        ignoreNextClipboardUpdate = $bindable(false),
    }: Props = $props();

    const clipboardMonitor = new ClipboardMonitor();
    let clipboardMonitorEnabled = $state(false);
    let clipboardIcon = $derived.by(() =>
        clipboardMonitorEnabled ? "clipboard-pulse" : "clipboard"
    );
    let clipboardButtonType = $derived.by(() =>
        clipboardMonitorEnabled ? "btn-success" : "btn-neutral"
    );

    function onKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter") {
            onSearch();
        }
        if (event.code === "KeyF" && event.ctrlKey) {
            inputElement.focus();
        }
    }

    function toggleClipboardMonitor() {
        clipboardMonitorEnabled = !clipboardMonitorEnabled;
        if (clipboardMonitorEnabled) {
            clipboardMonitor.start((text) => {
                if (ignoreNextClipboardUpdate) {
                    ignoreNextClipboardUpdate = false;
                    return;
                }
                value = text;
                onSearch();
            });
        } else {
            clipboardMonitor.stop();
        }
    }

    onMount(() => {
        if (autoTrigger && value) {
            onSearch();
        }
    });
</script>

<svelte:document onkeydown={onKeyDown} />

<div class="flex items-center gap-2 join">
    <input
        type="text"
        class="join-item input input-primary input-xl w-full"
        placeholder="Type a word to search..."
        bind:this={inputElement}
        bind:value
    />
    <button
        class="join-item btn btn-primary"
        onclick={onSearch}
        aria-label="Search"
    >
        <i class="bi bi-search"></i>
    </button>
    <button
        class="join-item btn {clipboardButtonType}"
        aria-label="Toggle clipboard monitor"
        title="Toggle clipboard monitor"
        onclick={toggleClipboardMonitor}
    >
        <i class="bi bi-{clipboardIcon}"></i>
    </button>
</div>
