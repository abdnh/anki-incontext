class InContext {
    constructor() {
        this.sentences = [];
    }

    clearSentences() {
        this.sentences = [];
    }

    _getSentenceElement(filterId) {
        return document.getElementById(
            `incontext-sentence-${filterId}`,
        );
    }

    refreshSentence(filterId) {
        const sentenceElement = this._getSentenceElement(filterId);
        const payload = {
            id: filterId,
            query: sentenceElement.dataset.query,
            lang: sentenceElement.dataset.lang,
            provider: sentenceElement.dataset.provider.split(","),
        };
        sentenceElement.innerHTML = "InContext: refreshing sentence...";
        pycmd(`incontext:refresh:${JSON.stringify(payload)}`);
    }

    addSentence(filterId, sentence) {
        this.sentences[filterId] = sentence;
    }

    renderSentence(filterId) {
        const sentenceElement = this._getSentenceElement(filterId);
        if (this.sentences[filterId]) {
            sentenceElement.innerHTML = this.sentences[filterId];
            sentenceElement.nextElementSibling.classList.remove("incontext-loading");
        }
    }

    saveAndRenderSentence(filterId, sentence) {
        const inContextIntervalID = setInterval(() => {
            const inContextSentenceElement = this._getSentenceElement(filterId);
            if (inContextSentenceElement) {
                clearInterval(inContextIntervalID);
                this.sentences[filterId] = sentence;
                inContextSentenceElement.innerHTML = sentence;
                inContextSentenceElement.nextElementSibling.classList.remove("incontext-loading");
            }
        }, 100);
    }

    setLoading(filterId) {
        const sentenceElement = this._getSentenceElement(filterId);
        sentenceElement.nextElementSibling.classList.add("incontext-loading");
    }
}

const incontext = new InContext();
