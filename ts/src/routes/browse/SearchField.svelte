<script lang="ts">
    let { onSearch, value = $bindable("") }: {
        onSearch: () => void;
        value: string;
    } = $props();

    function onKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter") {
            onSearch();
        }
    }
</script>

<div class="search-field">
    <input
        type="text"
        class="form-control"
        placeholder="Type a word to search..."
        bind:value={value}
        onkeydown={onKeyDown}
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
