<script lang="ts">
    import { Select } from "ankiutils";
    import { type ComponentProps } from "svelte";

    let { value = $bindable(), ...props }: ComponentProps<typeof Select> =
        $props();
</script>

<Select className="language-selector" bind:value {...props} />
