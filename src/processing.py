from review_text import ReviewText
from label import get_labels
from utils import flatten, keep_or_delete_label
labels_data, breakdowns_regardless = get_labels()


class CategorizeReviewTextLabel:
    def __init__(self, review_text, label):
        # create a Review Text instance
        self.review_text = ReviewText(review_text)

        self.label = label
        self.label_type = self.detect_label_type()
        if self.label_type != 0:
            self.label_data = labels_data[label]['data']
        self._keywords = []
        self.FOUND_KEYWORD = False

    @property
    def keywords(self):
        # flatten the keywords & remove duplicate keyword (use set) before return
        return list(set(flatten(self._keywords)))

    def get_label_data(self, key, flat=False):
        data = self.label_data[key]
        if flat:
            data = flatten(data)
            data = [value for value in data if value != '']
        return data

    def detect_label_type(self):
        return labels_data[self.label]['type']

    def find_keywords_no_sentiment(self, keywords, change_to_keywords):
        results = []
        for keywords_index, keywords_present in enumerate(keywords):
            for keyword in keywords_present:
                if keyword.lower() in self.review_text.text.lower():
                    corresponding_keyword = change_to_keywords[keywords_index]
                    results.append(corresponding_keyword)
        return results

    def add_otherwise_keyword(self):
        if 'OTHERWISE' in self.label_data:
            # get the keyword
            if len(self.label_data['OTHERWISE']) < 2:
                otherwise_keyword = self.label_data['OTHERWISE'][0]
            else:
                otherwise_keyword = self.label_data['OTHERWISE'][self.review_text.sentiment]
            self._keywords.append(otherwise_keyword)

    def processing(self):
        # label_type = 0 => not run
        if self.label_type == 0:
            return

        if self.label_type == 1:
            self.processing_type_1()
        elif self.label_type == 2:
            self.processing_type_2()
        elif self.label_type == 3:
            self.processing_type_3()
        else:
            self.processing_type_4()
        self.processing_regardless()

        # if there are no keyword in the review text, add OTHERWISE keywords
        if not self.FOUND_KEYWORD:
            self.add_otherwise_keyword()

    def processing_type_1(self, WORD_COMBINATION=False):
        FIND_KEYWORDS = self.get_label_data('FIND KEYWORDS')
        CORRESPONDING_KEYWORDS = self.get_label_data('RUN SENTIMENT ANALYSIS')
        OPPOSITE_WORDS = None

        for find_keywords_index, find_keywords in enumerate(FIND_KEYWORDS):
            for find_keyword in find_keywords:
                if find_keyword.lower() in self.review_text.text.lower():
                    # find correspoding keyword
                    corresponding_keyword = CORRESPONDING_KEYWORDS[find_keywords_index]

                    # loop through all sentences and find a sentence has that keyword
                    for sentence in self.review_text.sentences:
                        if find_keyword.lower() in sentence.text.lower():

                            # EXCEPTION: if label is fragrance and scent
                            if self.label == 'fragrance and scent':
                                OPPOSITE_WORDS = self.label_data['OPPOSITE WORDS']
                                for opposite_word in OPPOSITE_WORDS:
                                    k = '{0} {1}'.format(
                                        opposite_word, find_keyword.lower())
                                    if k in sentence.text.lower():
                                        self._keywords.append('fragrance free')

                            # Exception: eye;circles;dark;darkness;bag;hood
                            elif WORD_COMBINATION:
                                count = 0
                                for keyword in flatten(FIND_KEYWORDS):
                                    count += sentence.text.lower().count(keyword)
                                    if count >= 2:
                                        break

                                if count >= 2:
                                    self._keywords.append(
                                        corresponding_keyword[0])

                            else:
                                self._keywords.append(
                                    corresponding_keyword[sentence.sentiment])

                            self.FOUND_KEYWORD = True

        # EXCEPTION: if label is consistency and texture
        if self.label == 'consistency and texture':
            NO_SENTIMENT_KEYWORDS = self.get_label_data(
                'IF KEYWORDS PRESENT NO SENTIMENT', flat=True)
            for no_sentiment_keyword in NO_SENTIMENT_KEYWORDS:
                if no_sentiment_keyword in self.review_text.text:

                    KEEP_WORDS = self.get_label_data('UNLESS WORDS PRESENT')
                    DELETE_WORDS = self.get_label_data('IF LABELS PRESENT')
                    keep_consistency = keep_or_delete_label(review_text=self.review_text.text.lower(
                    ), KEEP_WORDS=KEEP_WORDS, DELETE_WORDS=DELETE_WORDS)
                    if keep_consistency:
                        new_keywords = self._keywords

                    # if consistency and texture not exists in review text, remove corresponding label
                    else:
                        new_keywords = [keyword for keyword in self.keywords if keyword !=
                                        'consistency (positive)' and keyword != 'consistency (negative)']
                    new_keywords.append(no_sentiment_keyword)
                    self._keywords = new_keywords
                    self.FOUND_KEYWORD = True

        # handle the exception
        if 'BREAKDOWN REGARDLESS OF SENTIMENT' in self.label_data:
            for keyword_breakdown_regardless in self.get_label_data('BREAKDOWN REGARDLESS OF SENTIMENT'):
                if keyword_breakdown_regardless in self.review_text.text:
                    self._keywords.append(keyword_breakdown_regardless)

        if 'IF WORDS PRESENT' in self.label_data:
            self._keywords.append(self.find_keywords_no_sentiment(self.get_label_data('IF WORDS PRESENT'),
                                                                  self.get_label_data('CHANGE TO')))

    def processing_type_2(self):
        FIND_KEYWORDS = self.label_data['IF KEYWORDS PRESENT NO SENTIMENT']
        CORRESPONDING_KEYWORDS = self.label_data['CHANGE TO']
        results = self.find_keywords_no_sentiment(
            FIND_KEYWORDS, CORRESPONDING_KEYWORDS)
        if len(results) > 0:
            self.FOUND_KEYWORD = True
        self._keywords.append(results)

        # EXCEPTION: nightly usage
        if self.label == 'nightly usage':
            if 'overnight' in self.keywords:
                if 'night' in self.keywords:
                    self._keywords = [
                        keyword for keyword in self.keywords if keyword != 'night']

    def processing_type_3(self):
        if 'IF KEYWORDS PRESENT' not in self.label_data:
            FIND_KEYWORDS = self.label_data['RUN SENTIMENT ANALYSIS ON WHOLE REVIEW']
            keyword = FIND_KEYWORDS[self.review_text.sentiment]
            self._keywords.append(keyword)
            self.FOUND_KEYWORD = True

        else:
            TAKE_FIRST = None
            KEYWORD_FOUND = {}

            # EXCEPTION: time of usage
            if self.label == 'time of usage':
                TAKE_FIRST = True

            # handle exception
            FIND_KEYWORDS = self.label_data['IF KEYWORDS PRESENT']
            CORRESPONDING_KEYWORDS = self.label_data['ASSIGN SENTIMENT']
            for find_keywords_index, find_keywords in enumerate(FIND_KEYWORDS):
                for find_keyword in find_keywords:
                    if find_keyword.lower() in self.review_text.text.lower():
                        # find correspoding keyword
                        if len(CORRESPONDING_KEYWORDS[find_keywords_index]) > 1:
                            corresponding_keyword = CORRESPONDING_KEYWORDS[
                                find_keywords_index][self.review_text.sentiment]
                        else:
                            corresponding_keyword = CORRESPONDING_KEYWORDS[find_keywords_index][0]

                        # if EXCEPTION: time of usage, try to find first keyword
                        if TAKE_FIRST:
                            position_found = self.review_text.text.lower().index(find_keyword.lower())

                            if KEYWORD_FOUND == {}:
                                KEYWORD_FOUND = {
                                    'keyword': corresponding_keyword, 'position': position_found}
                            else:
                                if position_found < KEYWORD_FOUND['position']:
                                    KEYWORD_FOUND = {
                                        'keyword': corresponding_keyword, 'position': position_found}
                        else:
                            self._keywords.append(corresponding_keyword)
                            self.FOUND_KEYWORD = True

            if TAKE_FIRST:
                if 'keyword' in KEYWORD_FOUND:
                    self._keywords.append(KEYWORD_FOUND['keyword'])
                    self.FOUND_KEYWORD = True

            if 'IF KEYWORDS PRESENT NO SENTIMENT' in self.label_data:
                for keywords_index, keywords in enumerate(self.label_data['IF KEYWORDS PRESENT NO SENTIMENT']):
                    for keyword in keywords:
                        if keyword.lower() in self.review_text.text.lower():
                            corresponding_keyword = self.label_data['CHANGE TO'][keywords_index]
                            self._keywords.append(corresponding_keyword)

    def processing_type_4(self):
        CHANGE_TO = self.label_data['CHANGE TO']

        for keyword in flatten(CHANGE_TO):
            self._keywords.append(keyword)

    def processing_regardless(self):
        for idx, breakdown in enumerate(breakdowns_regardless):
            FIND_KEYWORDS = breakdown['FOR THE WORD']

            if idx == 0:
                CORRESPONDING_KEYWORDS = breakdown['RUN SENTIMENT ANALYSIS']
                OPPOSITE_WORDS = breakdown['OPPOSITE WORDS']

                for find_keywords_index, find_keywords in enumerate(FIND_KEYWORDS):
                    for find_keyword in find_keywords:
                        if find_keyword.lower() in self.review_text.text.lower():
                            # find correspoding keyword

                            corresponding_keyword = CORRESPONDING_KEYWORDS[find_keywords_index]

                            # loop through all sentences and find a sentence has that keyword
                            for sentence in self.review_text.sentences:
                                if find_keyword.lower() in sentence.text.lower():
                                    FIND_OPPOSITE = False
                                    for opposite_word in OPPOSITE_WORDS:
                                        k = '{0} {1}'.format(
                                            opposite_word, find_keyword.lower())
                                        if k in sentence.text.lower():
                                            self._keywords.append(
                                                corresponding_keyword[0])
                                            FIND_OPPOSITE = True
                                    if not FIND_OPPOSITE:
                                        self._keywords.append(
                                            corresponding_keyword[sentence.sentiment])

                KEEP_WORDS = breakdown['UNLESS WORDS PRESENT']
                DELETE_WORDS = breakdown['IF LABELS PRESENT']
                keep_consistency = keep_or_delete_label(review_text=self.review_text.text.lower(
                ), KEEP_WORDS=KEEP_WORDS, DELETE_WORDS=DELETE_WORDS)
                if keep_consistency:
                    new_keywords = self._keywords

                # if consistency and texture not exists in review text, remove corresponding label
                else:
                    new_keywords = [keyword for keyword in self.keywords if keyword !=
                                    'consistency (positive)' and keyword != 'consistency (negative)']
                self._keywords = new_keywords

            if idx == 1:
                CORRESPONDING_KEYWORDS = breakdown['RERUN CATEGORY']

                temp_label = self.label
                temp_label_data = self.label_data
                temp_found_keyword = self.FOUND_KEYWORD

                for find_keywords_index, find_keywords in enumerate(FIND_KEYWORDS):
                    for find_keyword in find_keywords:
                        if find_keyword.lower() in self.review_text.text.lower():
                            self.label = flatten(CORRESPONDING_KEYWORDS)[
                                find_keywords_index]
                            self.label_data = labels_data[self.label]['data']
                            self.FOUND_KEYWORD = False
                            if find_keywords_index == 2:
                                self.processing_type_1(WORD_COMBINATION=True)
                            else:
                                self.processing_type_1()
                            if not self.FOUND_KEYWORD:
                                self.add_otherwise_keyword()

                self.FOUND_KEYWORD = temp_found_keyword
                self.label = temp_label
                self.label_data = temp_label_data

            if idx == 2:
                CORRESPONDING_KEYWORDS = flatten(
                    breakdown['RUN SENTIMENT ANALYSIS'])

                if self.label == 'cleansers and cleansing':
                    continue

                for keyword in flatten(FIND_KEYWORDS):
                    if keyword in self.review_text.text.lower():
                        for sentence in self.review_text.sentences:
                            if keyword.lower() in sentence.text.lower():
                                self._keywords.append(
                                    CORRESPONDING_KEYWORDS[sentence.sentiment])
