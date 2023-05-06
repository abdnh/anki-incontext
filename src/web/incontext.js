function InContextRefreshSentence(filterId) {
    const sentenceElement = document.getElementById(
        `incontext-sentence-${filterId}`
    );
    const payload = {
        id: filterId,
        query: sentenceElement.dataset.query,
        lang: sentenceElement.dataset.lang,
        provider: sentenceElement.dataset.provider,
    };
    sentenceElement.innerHTML = "InContext: refreshing sentence...";
    pycmd(`incontext:refresh:${JSON.stringify(payload)}`);
}
