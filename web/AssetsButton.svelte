<script>
    import { bridgeCommand } from "anki/bridgecommand";

    const { LabelButton } = anki.components;
</script>

<LabelButton on:click={() => bridgeCommand("assetManagerDialog")}>Assets...</LabelButton>
