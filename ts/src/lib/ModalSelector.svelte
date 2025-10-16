<script lang="ts">
    import Modal from "bootstrap/js/dist/modal";
    import { onMount } from "svelte";

    export interface Option {
        value: string;
        label: string;
    }

    interface Props {
        selectedOption: string;
        options: Option[];
        onSelected?: () => void;
    }

    let { selectedOption = $bindable(), onSelected, options }: Props =
        $props();
    let search = $state("");
    let filteredLanguages = $derived.by(() =>
        search
            ? options.filter(opt =>
                opt.value.toLowerCase().includes(search.toLowerCase())
                || opt.label.toLowerCase().includes(
                    search.toLowerCase(),
                )
            )
            : options
    );
    let selectedIndex = $derived.by(() => {
        for (let i = 0; i < filteredLanguages.length; i++) {
            if (isOptionSelected(filteredLanguages[i])) return i;
        }
        return -1;
    });

    let inputElement: HTMLInputElement;
    let modalElement: HTMLDivElement;
    let optionElements: HTMLButtonElement[] = $state([]);

    function isOptionSelected(option: Option) {
        return option.value.toLowerCase()
            === selectedOption
                .toLowerCase();
    }

    function selectOption(language: Option) {
        selectedOption = language.value;
        Modal.getOrCreateInstance(modalElement).hide();
        onSelected?.();
    }

    export function show() {
        const modal = new Modal(modalElement);
        modal.show();
    }

    onMount(() => {
        modalElement.addEventListener("shown.bs.modal", () => {
            inputElement.focus();
            if (selectedIndex >= 0) {
                optionElements[selectedIndex].scrollIntoView({
                    block: "center",
                });
            }
        });
    });
</script>

<div
    class="modal fade"
    tabindex="-1"
    aria-hidden="true"
    bind:this={modalElement}
>
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-body selectory-body">
                <input
                    bind:this={inputElement}
                    class="form-control search-field"
                    type="text"
                    bind:value={search}
                    placeholder="Search languages..."
                />
                <div class="options-container">
                    {#each filteredLanguages as language, i (language.value)}
                        <button
                            bind:this={optionElements[i]}
                            class={`option ${
                                isOptionSelected(language)
                                    ? "selected"
                                    : ""
                            }`}
                            onclick={() => selectOption(language)}
                        >
                            {language.label}
                        </button>
                    {/each}
                </div>
            </div>
        </div>
    </div>
</div>

<style lang="scss">
    .search-field {
        position: sticky;
        top: 2px;
        box-shadow: 0px 1px 5px 0px #898181;
    }
    .lang-button {
        background-color: #d9d9d9;
        border: none;
        border-radius: 4px;
        margin-inline: 4px;
        box-shadow: -1px 0px 5px 0px #898181;
    }
    .options-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
        padding: 0.5rem 0;
        gap: 8px;
    }

    .option {
        padding: 8px;
        border: 1px solid #efefef;
    }

    .option.selected {
        background-color: #8db5e7;
    }

    .option:hover {
        background-color: rgb(200, 223, 245);
    }
</style>
