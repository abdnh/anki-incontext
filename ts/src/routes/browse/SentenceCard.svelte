<script lang="ts">
    let { text, url, alternativeColor = false }: {
        text: string;
        url: string;
        alternativeColor: boolean;
    } = $props();
</script>

<div class={`card sentence-card ${alternativeColor ? "primary" : "secondary"}`}>
    <div class="card-body sentence-body">
        <div>{text}</div>
        <a href={url} target="_blank" aria-label="Open source">
            <i class="bi bi-globe"></i>
        </a>
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
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
    }
</style>
