import streamlit as st
import pandas as pd
import openai
import time
import yaml
import requests

## Read in credentials from YAML file
with open('credentials.yaml', 'r') as file:
    credentials = yaml.safe_load(file)

openai.api_type = credentials['api_type']
# Add API Base link 
api_base = ""
openai.api_key = credentials['api_key']
openai.api_version = credentials['api_version']
chatgpt_model_name = credentials['chatgpt_model_name']

## Beging Streamlit App
st.image(f'https://github.com/Martialgod1/RecommendGPT/blob/main/img/logo.png')

with st.sidebar.form('input'):

    st.markdown('# RecommendGPT')
     
    paper_title = st.text_input(
        "Paper Title",
        help = "What are you researching?",
        value = "Predicting changes in neutralizing antibody activity for SARS-CoV-2 XBB.1.5 using in silico protein modeling"
    )

    articles = st.file_uploader("Upload Articles Data", type={"csv", "txt"})
    if articles is not None:
        articles_df = pd.read_csv(articles)
        articles_df = articles_df[["Title", "URL"]]
        articles_df["Source"] = f'{articles_df["Title"]} (From: {articles_df["URL"]})'
    else:
        st.error('Please upload your articles as a CSV files with columns "Title" and "URL".')

    submit_button = st.form_submit_button(label='Extract data')

if submit_button:
    ## Check that text field is not empty
    if not paper_title.strip():
        st.error('Please enter a title or research topic.')
    else:
        with st.spinner(text = 'I\'m finding some articles for you…'):
            time.sleep(10)

        ## Create Title-URL text items
        articles_read =  ', '.join(articles_df['Source'].astype(str).values.flatten())

        ## Create question 
        question = '''Based on this list of my previously read scientific articles, please recommend other real journal articles I can cite for a paper titled "''' + paper_title + '''" and paste a link to the article so I can read it.

        Here is my list of journal articles I have read: ''' + articles_read


        ## Make Prompt object
        def create_prompt(system_message, messages):
            prompt = system_message
            for message in messages:
                prompt += f"\n<|im_start|>{message['sender']}\n{ message['text']}\n<|im_end|>"
            prompt += "\n<|im_start|>assistant\n"
            return (prompt)
        
        base_system_message = "You are a helpful assistant that recommends real scientific journal articles to read based on lists."
        system_message = f"<|im_start|>system\n{base_system_message.strip()}\n<|im_end|>"
        
        payload = {
            "messages": [
                {"role": "system", "content": base_system_message.strip()},
                {"role": "user", "content": question},
                {"role": "user", "content": "Please list in bullet points the recommended journal articles, their URLs, and why you are recommending them."}
            ],
            "max_tokens": 500,
            "temperature": 0.7,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "top_p": 0.95
        }
        
        headers = {
            "api-key": openai.api_key
        }
        response = requests.post(api_base, headers=headers, json=payload)
        
        response_content = response.json()['choices'][0]['message']['content']
        ## Main section content
        st.header('ChatGPT Article Recommendations')
        st.write('Paper Title: {}'.format(paper_title))

        st.write(response_content)

