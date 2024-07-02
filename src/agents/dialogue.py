class DialogueAgent:
    def __init__(self, llm, embedding):
        self.llm = llm
        self.embedding = embedding

    def invoke(self, text):
        response = self.llm(text)
        return response

    def stream(self, text):
        for chunk in self.llm.stream(text):
            yield chunk
