<script lang="ts">
    interface Props {
        keys: string[];
    }

    let { keys = $bindable([]) }: Props = $props();
    let keysDisplay = $derived.by(() => {
        let components = [];
        for (let key of keys) {
            if (key === " ") {
                key = "space";
            }
            components.push(key[0].toUpperCase() + key.slice(1));
        }
        return components.join(",");
    });

    function onKeydown(event: Event) {
        keys = [...keys, (event as KeyboardEvent).key];
        event.preventDefault();
    }

    function clearKeys() {
        keys = [];
    }
</script>

<div class="input-container">
    <input
        type="text"
        value={keysDisplay}
        onkeydown={onKeydown}
        placeholder="Press shortcut"
    >
    <button class="btn btn-danger" aria-label="Clear" onclick={clearKeys}>
        <i class="bi bi-x"></i>
    </button>
</div>

<style lang="scss">
    .input-container {
        display: flex;
        flex-direction: row;
        gap: 8px;

        input {
            cursor: pointer;
            box-shadow: rgb(189, 187, 187) 2px 2px 4px 0px;
            border: none;
            border-radius: 4px;
            padding: 8px;
            flex: 1;
        }
    }
</style>
