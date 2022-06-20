import nltk
from nltk.tokenize import sent_tokenize
from sentiment import classifier

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class Sentence:
    def __init__(self, text):
        self.text = text
        self._sentiment = None

    @property
    def sentiment(self):
        if self._sentiment == None:
            self._sentiment = self.sentiment_analysis()
        return self._sentiment

    def sentiment_analysis(self):
        # run sentiment analysis
        sentiment_result = classifier(self.text)[0]
        # return 0 if review_text is negative, otherwise 1
        if sentiment_result['label'] == 'Negative':
            return 1
        return 0


class ReviewText(Sentence):
    def __init__(self, text):
        self.text = text
        self.clean_review_text()
        self._sentiment = None
        self._sentences = None

    @property
    def sentences(self):
        if self._sentences == None:
            self._sentences = self.split_into_sentences()
        return self._sentences

    def clean_review_text(self):
        return self.text.replace('[This review was collected as part of a promotion.]', '')

    def split_into_sentences(self):
        sentences = []
        for sentence in sent_tokenize(self.text):
            sentences.append(Sentence(sentence))
        return sentences
