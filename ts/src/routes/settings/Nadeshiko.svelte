<script lang="ts">
    import type { ProviderOptions } from "./types";

    interface Props {
        allOptions?: ProviderOptions[];
    }
    let { allOptions = $bindable([]) }: Props = $props();
    let options = $derived<Record<string, string>>(
        allOptions.find(item => item.provider?.code === "nadeshiko")!
            .options,
    );
</script>

<form>
    <label class="form-control">
        <span class="label">API key</span>
        <input
            class="input w-full"
            type="password"
            bind:value={options["api_key"]}
        />
    </label>
</form>

<style lang="scss">
    .form-control {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;

        .label {
            grid-column: span 1 / span 1;
        }
        input {
            grid-column: span 3 / span 3;
            width: 100%;
        }
    }
</style>
