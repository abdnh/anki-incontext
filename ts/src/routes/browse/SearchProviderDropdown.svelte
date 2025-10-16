<script lang="ts">
    import Dropdown from "$lib/Dropdown.svelte";
    import type { SelectOption } from "$lib/SelectOptions.svelte";

    interface Props {
        label: string;
        options: SelectOption[];
        selectedOptions: string[];
        onSelected?: (value: string[]) => void;
    }

    let {
        label,
        options,
        selectedOptions = $bindable<string[]>([]),
        onSelected = () => {},
    }: Props = $props();
</script>

<Dropdown {label} {options} bind:selectedOptions multiple={true} {onSelected} />
