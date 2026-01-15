import type { Provider } from "$lib";

export interface ProviderOptions {
    provider: Provider;
    options: Record<string, any>;
}
