<script lang="ts">
    interface Props {
        error: string;
    }

    let { error }: Props = $props();

    $effect(() => {
        console.log("error", error);
    });
</script>

<div class="error">Error: {error}</div>

<style lang="scss">
    .error {
        text-align: center;
        font-size: 1.5em;
        color: rgb(247, 62, 62);
    }
</style>
