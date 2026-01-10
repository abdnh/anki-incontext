export {};

declare global {
    interface Window {
        qtWidgetId: string;
        incontext: Record<string, any>;
    }
}
