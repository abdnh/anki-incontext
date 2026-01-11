import type { PageLoad } from "./$types";

export const load: PageLoad = ({ url }) => {
    return {
        word: url.searchParams.get("word") ?? "",
        language: url.searchParams.get("language") ?? null,
        providers: url.searchParams.get("providers")?.split(",") ?? null,
        autoSearch: url.searchParams.get("auto") ? true : false,
    };
};
