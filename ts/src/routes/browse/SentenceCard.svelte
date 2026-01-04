<script lang="ts">
    let { text, url, provider, alternativeColor = false }: {
        text: string;
        url: string;
        provider: string;
        alternativeColor: boolean;
    } = $props();
</script>

<div class={`card sentence-card ${alternativeColor ? "primary" : "secondary"}`}>
    <div class="card-body sentence-body">
        <div>{text}</div>
        <a
            href={url}
            target="_blank"
            aria-label="Open source"
            class="sentence-source"
        >{provider}</a>
    </div>
</div>

<style lang="scss">
    .sentence-card.primary {
        background: var(--bs-dark-bg-subtle);
    }
    .sentence-card.secondary {
        background: var(--bs-primary-bg-subtle);
    }
    .sentence-body {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .sentence-source {
        font-size: smaller;
        align-self: flex-end;
    }
</style>
