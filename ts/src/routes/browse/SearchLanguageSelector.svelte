<script lang="ts">
    import type { Option } from "$lib/ModalSelector.svelte";
    import ModalSelector from "$lib/ModalSelector.svelte";

    interface Props {
        selectedLanguage: string;
        languages: Option[];
        onLanguageSelected?: () => void;
    }

    let {
        selectedLanguage = $bindable(),
        languages,
        onLanguageSelected,
    }: Props = $props();

    let selector: ModalSelector;
</script>

<button class="btn lang-button" onclick={() => selector.show()}>
    {selectedLanguage.toUpperCase()}
</button>

<ModalSelector
    bind:selectedOption={selectedLanguage}
    options={languages}
    onSelected={onLanguageSelected}
    bind:this={selector}
/>

<style lang="scss">
    .lang-button {
        background-color: #d9d9d9;
        border: none;
        border-radius: 4px;
        margin-inline: 4px;
        box-shadow: -1px 0px 5px 0px #898181;
    }
</style>
