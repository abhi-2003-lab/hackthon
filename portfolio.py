import pandas as pd
import chromadb
import uuid

class Portfolio:
    def __init__(self, file_path=r"D:\hackvers\my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        """Loads portfolio data into the vector database if empty."""
        if self.collection.count() == 0:  # Fix: Properly check if collection is empty
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=[row["Techstack"]],  # Fix: Needs to be a list
                    metadatas=[{"links": row["Links"]}],  # Fix: Needs to be a list
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        """Queries ChromaDB and returns portfolio links matching given skills."""
        results = self.collection.query(query_texts=[skills], n_results=2)

        # Fix: Ensure it extracts links correctly
        if "metadatas" in results and results["metadatas"]:
            return [meta["links"] for meta in results["metadatas"][0] if "links" in meta]

        return []  # Return empty list if no results found
