<script lang="ts">
    import { ModalSelector, type SelectOption } from "ankiutils";

    interface Props {
        selectedLanguage: string;
        languages: SelectOption[];
        onLanguageSelected?: () => void;
    }

    let {
        selectedLanguage = $bindable(),
        languages,
        onLanguageSelected,
    }: Props = $props();

    let selector: ModalSelector;
</script>

<button class="btn btn-neutral" onclick={() => selector.show()}>
    {selectedLanguage.toUpperCase()}
</button>

<ModalSelector
    bind:selectedOption={selectedLanguage}
    options={languages}
    onSelected={onLanguageSelected}
    bind:this={selector}
/>
