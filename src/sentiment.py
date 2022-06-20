# use nvidia gpu if avail|able
import streamlit as st
import torch
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer
from transformers import pipeline

device = 0 if torch.cuda.is_available() else -1

@st.experimental_singleton(show_spinner=False)
def get_classifier():
    model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = TFAutoModelForSequenceClassification.from_pretrained(model_name, from_pt=True)

    return pipeline('sentiment-analysis', model=model, tokenizer=tokenizer, device=device)


@st.experimental_memo(show_spinner=False)
def classifier(text):
    return get_classifier()(text)