<script lang="ts">
    import { tick } from "svelte";

    interface SelectOption {
        value: string;
        label: string;
    }

    interface Props {
        options: SelectOption[];
        value?: string;
        placeholder?: string;
        searchPlaceholder?: string;
        disabled?: boolean;
        clearable?: boolean;
    }

    let {
        options,
        value = $bindable(""),
        placeholder = "Select an option...",
        searchPlaceholder = "Search...",
        disabled = false,
        clearable = true,
    }: Props = $props();

    let searchTerm = $state("");
    let isOpen = $state(false);
    let highlightedIndex = $state(-1);

    let containerElement: HTMLDivElement;
    let inputElement: HTMLInputElement;
    let optionElements: HTMLButtonElement[] = $state([]);

    let filteredOptions = $derived(
        searchTerm
            ? options.filter(option =>
                option.label.toLowerCase().includes(
                    searchTerm.toLowerCase(),
                )
            )
            : options,
    );

    let selectedOption = $derived(
        options.find(option => option.value === value),
    );

    let displayValue = $derived(
        isOpen ? searchTerm : (selectedOption?.label || ""),
    );

    async function openDropdown() {
        if (disabled) return;
        isOpen = true;
        searchTerm = "";
        optionElements = [];
        const selectedIndex = selectedOption
            ? filteredOptions.findIndex(option =>
                option.value === selectedOption.value
            )
            : -1;
        highlightedIndex = selectedIndex;
        await tick();
        inputElement?.focus();
        if (selectedIndex >= 0) {
            scrollHighlightedIntoView();
        }
    }

    function closeDropdown() {
        isOpen = false;
        searchTerm = "";
        highlightedIndex = -1;
        optionElements = [];
    }

    function selectOption(option: SelectOption) {
        value = option.value;
        closeDropdown();
    }

    function clearSelection() {
        value = "";
        searchTerm = "";
        inputElement?.focus();
    }

    async function scrollHighlightedIntoView() {
        await tick();
        if (highlightedIndex >= 0 && optionElements[highlightedIndex]) {
            optionElements[highlightedIndex].scrollIntoView({
                behavior: "smooth",
                block: "nearest",
            });
        }
    }

    function handleKeydown(event: KeyboardEvent) {
        if (!isOpen) {
            if (
                event.key === "Enter" || event.key === " "
                || event.key === "ArrowDown"
            ) {
                event.preventDefault();
                openDropdown();
            }
            return;
        }

        switch (event.key) {
            case "Escape":
                event.preventDefault();
                closeDropdown();
                break;
            case "ArrowDown":
                event.preventDefault();
                highlightedIndex = Math.min(
                    highlightedIndex + 1,
                    filteredOptions.length - 1,
                );
                scrollHighlightedIntoView();
                break;
            case "ArrowUp":
                event.preventDefault();
                highlightedIndex = Math.max(highlightedIndex - 1, -1);
                scrollHighlightedIntoView();
                break;
            case "Enter":
                event.preventDefault();
                if (
                    highlightedIndex >= 0
                    && filteredOptions[highlightedIndex]
                ) {
                    selectOption(filteredOptions[highlightedIndex]);
                }
                break;
            case "Tab":
                closeDropdown();
                break;
        }
    }

    function handleClickOutside(event: MouseEvent) {
        if (
            containerElement
            && !containerElement.contains(event.target as Node)
        ) {
            closeDropdown();
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

<div class="select-container" bind:this={containerElement}>
    <div class="input-group">
        <input
            bind:this={inputElement}
            class="form-control"
            type="text"
            value={displayValue}
            placeholder={isOpen ? searchPlaceholder : placeholder}
            readonly={!isOpen}
            {disabled}
            oninput={(e) => {
                if (isOpen) {
                    searchTerm = e.currentTarget.value;
                    highlightedIndex = -1;
                    optionElements = [];
                }
            }}
            onclick={openDropdown}
            onkeydown={handleKeydown}
        />

        <div class="control-buttons btn-group" role="group">
            {#if clearable && value && !disabled}
                <button
                    type="button"
                    class="btn btn-outline-secondary clear-btn"
                    onclick={clearSelection}
                    aria-label="Clear selection"
                >
                    <i class="bi bi-x"></i>
                </button>
            {/if}
            <button
                type="button"
                class="btn btn-outline-secondary dropdown-toggle"
                class:disabled
                onclick={() => isOpen ? closeDropdown() : openDropdown()}
                aria-label="Toggle dropdown"
            >
                <i class="bi bi-chevron-{isOpen ? 'up' : 'down'}"></i>
            </button>
        </div>
    </div>

    {#if isOpen}
        <div
            class="dropdown-menu show w-100 mt-1"
            style="position: absolute; z-index: 1000"
        >
            {#if filteredOptions.length === 0}
                <div class="dropdown-item-text text-muted">
                    No options found
                </div>
            {:else}
                {#each filteredOptions as option, index (option.value)}
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
                {/each}
            {/if}
        </div>
    {/if}
</div>

<style>
    .select-container {
        position: relative;
    }

    .dropdown-menu {
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

    .form-control[readonly]:not([disabled]) {
        cursor: pointer;
    }
</style>
