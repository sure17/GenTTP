# GenTTP

```shell
conda create -n GenTTP python=3.11.9
conda activate GenTTP
pip install -r requirements.txt

streamlit run webui.py
```

## Chatbot
Chatbot Demo in: https://genttp.streamlit.app/ that provides malware analysis to users.

## Appendix

This PDF document contains supplementary materials that expand on key details from the paper, including:

### 1. Tables with Detailed Information
- **Table 1**: Describes the context of deceptive and execution attack vectors (AVCs) used in the malware analysis.
- **Table 2 - Table 5**: Provide detailed security analysis reports, summarized interpreted malware data, and metadata for specific packages.
- **Table 6 - Table 9**: Includes prompts used for malware behavior analysis, generation, and detection in relation to various tasks such as decompression and malware package identification.

### 2. Prompts
- The document outlines prompts used in generating the AVCs of malware packages leveraging large language models (LLMs). These prompts are designed to guide the behavior of analysis agents and chatbots in identifying and understanding the malicious activities in open-source software.

These materials serve as a reference for the methodology and experimental results discussed in the paper and provide in-depth insights into the experimental setup and data used in our research.