<script lang="ts">
    import SelectOptions, {
        type SelectOption,
    } from "./SelectOptions.svelte";

    interface Props {
        label: string;
        options: SelectOption[];
        selectedOptions: string[];
        multiple?: boolean;
        onSelected?: (value: string[]) => void;
    }

    let {
        label,
        options,
        selectedOptions = $bindable<string[]>([]),
        multiple = false,
        onSelected = () => {},
    }: Props = $props();

    let isOpen = $state(false);
    let containerElement: HTMLDivElement;
    let selectOptionsComponent: SelectOptions | undefined = $state();

    function handleClickOutside(event: MouseEvent) {
        if (
            containerElement
            && !containerElement.contains(event.target as Node)
        ) {
            selectOptionsComponent?.closeDropdown();
        }
    }

    $effect(() => {
        if (isOpen) {
            document.addEventListener("click", handleClickOutside);
            return () =>
                document.removeEventListener(
                    "click",
                    handleClickOutside,
                );
        }
    });
</script>

<div class="dropdown-container" bind:this={containerElement}>
    <button class="btn" onclick={() => isOpen = !isOpen}>
        <span>{label}</span>
        <i class="bi bi-chevron-{isOpen ? 'up' : 'down'}"></i>
    </button>
    {#if isOpen}
        <SelectOptions
            bind:this={selectOptionsComponent}
            {options}
            bind:selectedOptions
            {multiple}
            {onSelected}
            bind:isOpen
        />
    {/if}
</div>
<style lang="scss">
    .dropdown-container {
        position: relative;
    }
</style>
