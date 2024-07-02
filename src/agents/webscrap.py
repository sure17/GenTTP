import os
import time
from tqdm import tqdm
import pandas as pd 

from langchain_openai import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_core.prompts import ChatPromptTemplate


failed_data = []

llm = ChatOpenAI(temperature=0, model="gpt-4", openai_api_key="YOUR_API_KEY")

schema = {
    "properties": {
        "malicious_package_actions": {"type": "string"},
        "malicious_package_name": {"type": "string"},
    },
    "required": ["malicious_package_name", "malicious_package_actions"],
}

template = "Extract the name of the malicious pypi package present in {content} and the key description, and the output is malicious_package_name and malicious_package_actions"

prompt = ChatPromptTemplate.from_template(template)


def extract(content: str, schema: dict):
    return create_extraction_chain(schema=schema, prompt=prompt, llm=llm).invoke(content)


def scrape_with_playwright(urls, schema):
    try:
        loader = AsyncChromiumLoader(urls)
        docs = loader.load()
    except:
        print('error')
        return

    if not docs:
        print(f"{urls}, No documents loaded.")
        return

    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(docs)

    if not docs_transformed:
        print("Document transformation failed.")
        return

    print(f"Extracting content with LLM, {urls}")

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_overlap=0)
    splits = splitter.split_documents(docs_transformed)

    if not splits:
        print(f"{urls}, No content available after splitting.")
        failed_data.append(urls)
        return

    extracted_content = extract(schema=schema, content=splits[0].page_content)
    return extracted_content["text"]


def saved_to_excel(extracted_content, saved_path):
    data = []
    for item in extracted_content:
        data.append({'url': urls[0], 'package_name': item['malicious_package_name'], 'package_action': item['malicious_package_actions']})

    new_df = pd.DataFrame(data)

    if os.path.isfile(saved_path):
        with pd.ExcelWriter(saved_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            existing_df = pd.read_excel(saved_path, engine='openpyxl')
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_excel(writer, index=False)
    else:
        new_df.to_excel(saved_path, index=False)


def main():
    df = pd.read_excel('./report_url_unique_2.xlsx', engine='openpyxl')

    for item in tqdm(df['Url'], desc='Processing URLs'):
        urls = [item]
        extracted_content = scrape_with_playwright(urls, schema=schema)
        saved_path = './report_url_extract_content_0124_v5.xlsx'
        try:
            saved_to_excel(extracted_content, saved_path)
        except:
            print('error')
        time.sleep(10)

    print(failed_data)


if __name__ == "__main__":
    main()