<script lang="ts">
    let {
        text,
        url,
        provider,
        alternativeColor = false,
    }: {
        text: string;
        url: string;
        provider: string;
        alternativeColor: boolean;
    } = $props();
</script>

<div
    class={`sentence-card card bg-base-100 ${
        alternativeColor ? "bg-base-200" : "bg-base-300"
    }`}
>
    <div class="card-body flex flex-col gap-2">
        <div class="text-xl">{text}</div>
        <a
            href={url}
            target="_blank"
            aria-label="Open source"
            class="link link-primary self-end"
        >{provider}</a>
    </div>
</div>
