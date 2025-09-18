import type { PageLoad } from "./$types";

export const load: PageLoad = ({ url }) => {
    return {
        nids: url.searchParams.get("nids")?.split(",").map(Number) ?? [],
    };
};
