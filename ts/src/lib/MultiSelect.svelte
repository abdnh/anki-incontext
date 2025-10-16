<script lang="ts">
    import BaseSelect from "./BaseSelect.svelte";
    import { type SelectOption } from "./SelectOptions.svelte";

    interface Props {
        id?: string;
        options: SelectOption[];
        selectedOptions: string[];
        placeholder?: string;
        searchPlaceholder?: string;
        disabled?: boolean;
        clearable?: boolean;
        onSelected?: (options: string[]) => void;
    }

    let {
        id,
        options,
        selectedOptions = $bindable<string[]>([]),
        placeholder,
        searchPlaceholder,
        disabled = false,
        clearable = true,
        onSelected = () => {},
    }: Props = $props();
</script>

<BaseSelect
    id={id}
    options={options}
    bind:selectedOptions={selectedOptions}
    placeholder={placeholder}
    searchPlaceholder={searchPlaceholder}
    disabled={disabled}
    clearable={clearable}
    multiple={true}
    onSelected={onSelected}
/>
