from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_text_splits(text, chunk_size=1500, overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
    )
    splits = splitter.create_documents([text])
    return splits
