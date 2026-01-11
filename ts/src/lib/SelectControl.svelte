<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        children?: Snippet;
        label: string;
    }
    const { children, label }: Props = $props();
</script>

<label class="form-control">
    <span class="label">{label}</span>
    <div class="input-container">
        {@render children?.()}
    </div>
</label>

<style lang="scss">
    .form-control {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;

        .label {
            grid-column: span 1 / span 1;
        }
        .input-container,
        :global(input) {
            grid-column: span 3 / span 3;
            width: 100%;
        }
        .input-container {
            & > :global(*) {
                width: 100%;
            }

            :global(input) {
                flex-grow: 1;
            }
        }
    }
</style>
