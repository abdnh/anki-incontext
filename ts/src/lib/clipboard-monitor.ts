import { client } from "$lib";
import { Code, ConnectError } from "@connectrpc/connect";

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
            if (text.trim() && text !== this.text) {
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
        try {
            return (
                await client.getClipboardText({}, { timeoutMs: this.interval })
            ).text;
        } catch (err) {
            if (
                err instanceof ConnectError
                && err.code === Code.DeadlineExceeded
            ) {
                return "";
            }
            throw err;
        }
    }
}
