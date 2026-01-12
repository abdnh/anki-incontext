<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        children?: Snippet;
        label: string;
    }
    const { children, label }: Props = $props();

    let inputContainer = $state<HTMLDivElement>();

    function handleLabelClick(event: MouseEvent) {
        if (inputContainer?.contains(event.target as Node)) {
            // If the click was inside the input container, prevent the label's default behavior from reopening the selector
            event.preventDefault();
        }
    }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<label class="form-control" onclick={handleLabelClick}>
    <span class="label">{label}</span>
    <div class="input-container" bind:this={inputContainer}>
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
