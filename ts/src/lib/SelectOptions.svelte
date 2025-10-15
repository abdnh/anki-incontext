<script lang="ts">
    export interface SelectOption {
        value: string;
        label: string;
    }

    interface Props {
        options: SelectOption[];
        selectedOptions: string[];
        multiple?: boolean;
        isOpen?: boolean;
        onSelected?: (value: string[]) => void;
        onOpenDropdown?: () => void;
        onCloseDropdown?: () => void;
    }

    let {
        options,
        selectedOptions = $bindable<string[]>([]),
        multiple = false,
        isOpen = $bindable(false),
        onSelected,
        onOpenDropdown,
        onCloseDropdown,
    }: Props = $props();

    let optionElements: (HTMLButtonElement | HTMLInputElement)[] =
        $state([]);
    let highlightedIndex = $state(-1);

    export async function openDropdown() {
        isOpen = true;
        optionElements = [];
        const selectedIndex = selectedOptions[0]
            ? options.findIndex(option =>
                option.value === selectedOptions[0]
            )
            : -1;
        highlightedIndex = selectedIndex;
        onOpenDropdown?.();
    }

    export function closeDropdown() {
        isOpen = false;
        highlightedIndex = -1;
        optionElements = [];
        onCloseDropdown?.();
    }

    export function selectOption(option: SelectOption) {
        if (multiple) {
            if (selectedOptions.includes(option.value)) {
                selectedOptions = selectedOptions.filter(o =>
                    o !== option.value
                );
            } else {
                selectedOptions.push(option.value);
            }
        } else {
            selectedOptions = [option.value];
            closeDropdown();
        }
        onSelected?.(selectedOptions);
    }
</script>

<div
    class="dropdown-menu show min mt-1"
    style={`position: absolute; z-index: 1000;`}
>
    {#if options.length === 0}
        <div class="dropdown-item-text text-muted">
            No options found
        </div>
    {:else}
        {#each options as option, index (option.value)}
            {#if multiple}
                <label class="dropdown-item">
                    <input
                        bind:this={optionElements[index]}
                        type="checkbox"
                        checked={selectedOptions.includes(option.value)}
                        onclick={() => selectOption(option)}
                        onmouseenter={() => highlightedIndex = index}
                    >
                    {option.label}
                </label>
            {:else}
                <button
                    bind:this={optionElements[index]}
                    type="button"
                    class="dropdown-item"
                    class:active={index === highlightedIndex}
                    onclick={() => selectOption(option)}
                    onmouseenter={() => highlightedIndex = index}
                >
                    {option.label}
                </button>
            {/if}
        {/each}
    {/if}
</div>

<style lang="scss">
    .dropdown-menu {
        min-width: 100%;
        max-height: 200px;
        overflow-y: auto;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.175);
    }

    .dropdown-item {
        cursor: pointer;
    }

    .dropdown-item.active {
        background-color: var(--bs-primary);
        color: var(--bs-primary-text);
    }
</style>
