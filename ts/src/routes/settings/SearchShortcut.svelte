<script lang="ts">
    import { KeyboardInput } from "ankiutils";

    interface Props {
        keys: string[];
    }

    let { keys = $bindable([]) }: Props = $props();
</script>

<KeyboardInput bind:keys />
