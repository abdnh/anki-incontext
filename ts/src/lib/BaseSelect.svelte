<script lang="ts">
    import { tick } from "svelte";
    import SelectOptions, {
        type SelectOption,
    } from "./SelectOptions.svelte";

    interface Props {
        id?: string;
        options: SelectOption[];
        selectedOptions: string[];
        placeholder?: string;
        searchPlaceholder?: string;
        disabled?: boolean;
        clearable?: boolean;
        multiple?: boolean;
        onSelected?: (value: string[]) => void;
    }

    let {
        id,
        options,
        selectedOptions = $bindable<string[]>([]),
        placeholder = "Select an option...",
        searchPlaceholder = "Search...",
        disabled = false,
        clearable = false,
        multiple = false,
        onSelected = () => {},
    }: Props = $props();

    let searchTerm = $state("");
    let isOpen = $state(false);
    let highlightedIndex = $state(-1);

    let containerElement: HTMLDivElement;
    let inputElement: HTMLInputElement;
    let optionElements: (HTMLButtonElement | HTMLInputElement)[] =
        $state([]);

    let filteredOptions = $derived(
        searchTerm
            ? options.filter(option =>
                option.label.toLowerCase().includes(
                    searchTerm.toLowerCase(),
                )
            )
            : options,
    );

    let displayValue = $derived(
        isOpen
            ? searchTerm
            : (selectedOptions.map(option =>
                options.find(o => o.value === option)?.label
            ).filter(o => o?.trim()).join(", ") || ""),
    );

    let selectOptionsComponent: SelectOptions | undefined = $state();

    async function onOpenDropdown() {
        searchTerm = "";
        await tick();
        inputElement?.focus();
        if (highlightedIndex >= 0) {
            scrollHighlightedIntoView();
        }
    }

    function onCloseDropdown() {
        searchTerm = "";
    }

    function clearSelection() {
        if (multiple) {
            selectedOptions = [];
        } else {
            selectedOptions = [""];
        }
        searchTerm = "";
        inputElement?.focus();
        onSelected(selectedOptions);
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
                selectOptionsComponent?.openDropdown();
            }
            return;
        }

        switch (event.key) {
            case "Escape":
                event.preventDefault();
                selectOptionsComponent?.closeDropdown();
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
                    selectOptionsComponent?.selectOption(
                        filteredOptions[highlightedIndex],
                    );
                }
                break;
            case "Tab":
                selectOptionsComponent?.closeDropdown();
                break;
        }
    }

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

<div class="select-container" bind:this={containerElement}>
    <div class="input-group input-container">
        <input
            bind:this={inputElement}
            id={id}
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
            onclick={() => isOpen = true}
            onkeydown={handleKeydown}
        />

        <div class="control-buttons btn-group" role="group">
            {#if clearable && isOpen && selectedOptions.length > 0
                    && !disabled}
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
                class="btn btn-outline-secondary"
                class:disabled
                onclick={() => isOpen = !isOpen}
                aria-label="Toggle dropdown"
            >
                <i class="bi bi-chevron-{isOpen ? 'up' : 'down'}"></i>
            </button>
        </div>
    </div>

    {#if isOpen}
        <SelectOptions
            bind:this={selectOptionsComponent}
            bind:isOpen
            options={filteredOptions}
            bind:selectedOptions
            {multiple}
            {onSelected}
            {onOpenDropdown}
            {onCloseDropdown}
        />
    {/if}
</div>

<style lang="scss">
    .select-container {
        position: relative;
    }
    .input-container {
        gap: 0.5rem;
    }

    .form-control[readonly]:not([disabled]) {
        cursor: pointer;
    }
</style>
