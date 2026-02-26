from __future__ import annotations

import requests
import streamlit as st

st.set_page_config(page_title='RAG Support UI', page_icon='💬')
st.title('AI Customer Support (RAG)')

api_url = st.text_input('API URL', value='http://localhost:8000/ask')
question = st.text_area('Question', placeholder='How do I reset my account password?')
customer_id = st.text_input('Customer ID (optional)')
ticket_id = st.text_input('Ticket ID (optional)')

if st.button('Ask') and question.strip():
    payload = {'question': question, 'customer_id': customer_id or None, 'ticket_id': ticket_id or None}
    with st.spinner('Requesting answer...'):
        try:
            response = requests.post(api_url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            st.subheader('Answer')
            st.write(data['answer'])
            st.metric('Confidence', f"{data['confidence']:.2f}")
            st.metric('Latency (ms)', data['latency_ms'])
            st.write('Handoff required:', data['handoff_required'])
            st.subheader('Citations')
            st.json(data['citations'])
        except Exception as exc:
            st.error(f'Failed to query API: {exc}')
