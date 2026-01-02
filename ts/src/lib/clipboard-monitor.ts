import { client } from "$lib";

export class ClipboardMonitor {
    private interval = 1000;
    private text = "";
    private intervalId: ReturnType<typeof setInterval> | null = null;

    start(changeCallback: (text: string) => void) {
        if (this.intervalId) {
            return;
        }
        this.intervalId = setInterval(async () => {
            const text = await this.getClipboardText();
            if (text !== this.text) {
                this.text = text;
                changeCallback(text);
            }
        }, this.interval);
    }

    stop() {
        if (this.intervalId) {
            clearTimeout(this.intervalId);
            this.intervalId = null;
        }
    }

    private async getClipboardText() {
        return (await client.getClipboardText({})).text;
    }
}
