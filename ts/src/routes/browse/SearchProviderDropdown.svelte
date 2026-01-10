<script lang="ts">
    import type { SelectOption } from "ankiutils";
    import { Dropdown } from "ankiutils";

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
