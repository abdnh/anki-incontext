<script lang="ts">
    import KeyboardInput from "$lib/KeyboardInput.svelte";

    interface Props {
        keys: string[];
    }

    let { keys = $bindable([]) }: Props = $props();
</script>

<KeyboardInput bind:keys />
