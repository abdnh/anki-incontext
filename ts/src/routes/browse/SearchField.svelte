<script lang="ts">
    import { onMount } from "svelte";

    let inputElement: HTMLInputElement;

    let { onSearch, value = $bindable(""), autoTrigger = false }: {
        onSearch: () => void;
        value: string;
        autoTrigger: boolean;
    } = $props();

    function onKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter") {
            onSearch();
        }
        if (event.code === "KeyF" && event.ctrlKey) {
            inputElement.focus();
        }
    }

    onMount(() => {
        if (autoTrigger && value) {
            onSearch();
        }
    });
</script>

<svelte:document onkeydown={onKeyDown}></svelte:document>

<div class="search-field">
    <input
        type="text"
        class="form-control"
        placeholder="Type a word to search..."
        bind:this={inputElement}
        bind:value={value}
    />
    <button class="btn btn-primary" onclick={onSearch} aria-label="Search">
        <i class="bi bi-search"></i>
    </button>
</div>

<style lang="scss">
    .search-field {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
</style>
