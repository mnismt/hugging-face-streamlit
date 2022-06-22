import os
import streamlit as st
import pandas as pd
import numpy as np

CATEGORIES = ['application and absorption', 'anti-ageing/wrinkles', 'blemished skin', 'blotchiness', 'cleansers and cleansing',
              'clear skin (type)', 'combination skin (type)', 'congested or acne prone skin', 'dark eye circles', 'dewy', 'dullness',
              'inflammation', 'as/ds/pig/disc (age spots, dark spots, discoloration, and pigmentation)', 'puffiness', 'redness',
              'scarring', 'pores', 'eczema', 'skin tightness', 'fragrance and scent', 'residue, white cast ', 'matte finish',
              'brightening, shine, glow etc', 'plumping', 'normal skin (type)', 'nourishing and refreshing', 'greasiness', 'consistency and texture',
              'dry skin and patches', 'tanning', 'dried quickly', 'spots', 'lips', 'highlighted imperfections', 'addition of products',
              'damaged skin', 'color', 'dark or brown skin', 'no changes', 'lips', 'season of usage', 'sun protection/SPF', 'pills',
              'nightly usage', 'comforting, calming, soothing, and cooling', 'hydration/moisture', 'supple', 'oily skin', 'pimples,breakout and acne',
              'tone and complexion', 'smooth, soft and silky skin', 'irritation', 'sensitive skin (type)', 'time of usage']

# 0 is the command has only 1 value, 1 is many values
COMMANDS = {'FIND KEYWORDS': 1, 'RUN SENTIMENT ANALYSIS': 1, 'OTHERWISE': 0,
            'BREAKDOWN REGARDLESS OF SENTIMENT': 0, 'IF WORDS PRESENT': 1, 'CHANGE TO': 1,
            'IF KEYWORDS PRESENT NO SENTIMENT': 1, 'RUN SENTIMENT ANALYSIS ON WHOLE REVIEW': 0,
            'IF KEYWORDS PRESENT': 1, 'ASSIGN SENTIMENT': 1,
            # exception
            'OPPOSITE WORDS': 0, 'RERUN CATEGORY': 1, 'EXCEPTION': 0, "EXCEPTION - CATEGORY PRESENT DON'T RUN": 0,
            'FOR THE WORD': 1, 'EXCEPTION - DELETE': 0, 'UNLESS WORDS PRESENT': 0, 'IF LABELS PRESENT': 1}

TYPES = {'FIND KEYWORDS': 1, 'IF KEYWORDS PRESENT NO SENTIMENT': 2, 'RUN SENTIMENT ANALYSIS ON WHOLE REVIEW': 3,
         'CHANGE TO': 4, 'FOR THE WORD': 5}

keywords_data = pd.read_excel(os.path.join(os.path.dirname(
    __file__), './data/hugging.xlsx'), sheet_name='Sheet1')


def handle_label(review_row):

    LABEL_COMMAND = None
    LABEL_VALUE = None

    label = {}

    for cell in review_row[1:]:

        if cell is np.nan:
            break

        # If cell is command
        if cell.isupper():
            LABEL_COMMAND = ' '.join(cell.split())
            LABEL_VALUE = COMMANDS[LABEL_COMMAND]
            continue

        if LABEL_VALUE == 0:
            label[LABEL_COMMAND] = cell.split(';')
        else:
            if LABEL_COMMAND not in label:
                label[LABEL_COMMAND] = []
            label[LABEL_COMMAND].append(cell.split(';'))

    return label


@st.experimental_memo(show_spinner=False)
def get_labels():
    labels_data = {}
    breakdowns_regardless = []
    for idx, row in keywords_data.iterrows():

        label = row['Label']

        if 'Breakdown regardless of category present' in label:
            label = 'Breakdown regardless of category present - {0}'.format(
                idx)
            LABEL_TYPE = TYPES[row[1]]
            breakdowns_regardless.append(handle_label(row))
            continue

        if not isinstance(row[1], str):
            labels_data[label] = {'type': 0}
            continue

        LABEL_TYPE = TYPES[row[1]]
        labels_data[label] = {'type': LABEL_TYPE, 'data': handle_label(row)}

    return labels_data, breakdowns_regardless
