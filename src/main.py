import streamlit as st
from processing import CategorizeReviewTextLabel
from label import CATEGORIES
import pandas as pd


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

    st.subheader('Final result:')
    st.write(list(set(final_keywords)))
