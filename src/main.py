import streamlit as st
from processing import CategorizeReviewTextLabel
from label import CATEGORIES
import pandas as pd
from review_text import ReviewText


@st.experimental_memo
def get_keywords(review_text, label):
    categorized_review_text = CategorizeReviewTextLabel(review_text, label)
    categorized_review_text.processing()
    return categorized_review_text.keywords


st.title('Hugging Face Test')
review_text = st.text_area(label="Review text", key='review_text')
labels = st.multiselect(
    'Labels (multi-select)',
    CATEGORIES
)

if st.button('Process'):

    if not review_text:
        st.error('Please input the review text')
        st.stop()
    if len(labels) < 1:
        st.error('Please choose at least one label')
        st.stop()

    review_instance = ReviewText(review_text)

    st.subheader('Sentiment Analysis')
    review_sentiment = 'Negative'
    if review_instance.sentiment == 0:
        review_sentiment = 'Positive'
    st.markdown("By review text: **{0}**".format(review_sentiment))

    st.write("By each sentence: ")

    def get_sentiment_text(
        sentiment): return "Positive" if sentiment == 0 else "Negative"
    sentences_sentiment_text = ["- {0}: **{1}**".format(sentence.text,
                                                        get_sentiment_text(sentence.sentiment)) for sentence in review_instance.sentences]
    st.markdown('\n'.join(sentences_sentiment_text))

    final_keywords = []
    results_df = pd.DataFrame({'label': labels})
    for idx_label, label in enumerate(labels):
        keywords = get_keywords(review_text, label)
        final_keywords += keywords
        for idx_keyword, keyword in enumerate(keywords):
            keyword_column = 'Keyword {0}'.format(idx_keyword + 1)
            if keyword_column not in results_df.columns:
                results_df[keyword_column] = ''
            results_df.loc[idx_label, keyword_column] = keyword

    st.subheader('Keywords for each label')
    st.dataframe(results_df)

    st.subheader('Final results:')
    st.write(list(set(final_keywords)))
