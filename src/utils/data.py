import os
import json
import time
from langchain_core.documents import Document


def add_document(collection, embedding, input_dir):
    files = os.listdir(input_dir)
    lenght = len(files)
    for i in range(lenght):
        file = files[i]
        if file.endswith(".json"):
            file_path = os.path.join(input_dir, file)
            with open(file_path) as f:
                data = json.load(f)

            package_name = data.get("package_name", "")
            version = data.get("version", "")
            ttp = data.get("TTP", "")
            ecosystem = data.get("ecosystem", "")
            analysis_process = data.get("analysis_process", {})

            document_content = {
                "package_name": package_name,
                "version": version,
                "TTP": ttp,
                "ecosystem": ecosystem,
                "analysis_process": analysis_process,
            }

            document = Document(page_content=json.dumps(document_content))

            embeddings = embedding.embed_documents(document.page_content)

            collection.add_documents(documents=[document], embeddings=[embeddings])
            print("Done: ", file)
            yield i, lenght
            time.sleep(5)  # To avoid rate limiting
