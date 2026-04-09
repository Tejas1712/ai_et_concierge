"""
Ingest ET catalog data into FAISS vector store.
Run this script once whenever you add or update data.

Usage:
    python ingest.py
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"token": os.getenv("HF_TOKEN")}  # ← add this
)
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def load_catalog(catalog_path: str = None) -> list:
    """Load products from et_catalog.json"""
    if catalog_path is None:
        catalog_path = Path(__file__).parent / "data" / "et_catalog.json"

    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["products"]


def convert_to_documents(products: list) -> list[Document]:
    """
    Convert each product into a LangChain Document.
    Each document contains a rich text description + metadata.
    """
    documents = []

    for product in products:
        # Build a rich text description for embedding
        content = f"""
Product: {product.get('product_name') or product.get('name')}
Description: {product.get('core_benefit') or product.get('description')}
Target Audience: {', '.join(product.get('target_audience', []))}
Categories: {', '.join(product.get('includes') or product.get('categories', []))}
Keywords: {', '.join(product.get('trigger_keywords', []))}
Risk Profile: {', '.join(product.get('risk_profile', []))}
URL: {product.get('url', '')}
        """.strip()

        # Store metadata for retrieval
        metadata = {
            "id": product.get("product_id") or product.get("id"),
            "name": product.get("product_name") or product.get("name"),
            "url": product.get("url", ""),
            "cta_text": product.get("cta_text", ""),
        }

        documents.append(Document(page_content=content, metadata=metadata))

    return documents


def main():
    print(" Starting ingestion...")

    # Step 1 — Load catalog
    print(" Loading ET catalog...")
    products = load_catalog()
    print(f"    Loaded {len(products)} products")

    # Step 2 — Convert to Documents
    print(" Converting to documents...")
    documents = convert_to_documents(products)
    print(f"    Created {len(documents)} documents")

    # Step 3 — Load embedding model
    print(" Loading HuggingFace embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("    Embeddings loaded")

    # Step 4 — Create FAISS vector store
    print(" Creating FAISS vector store...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    print("    Vector store created")

    # Step 5 — Save locally
    save_path = Path(__file__).parent / "data" / "vectorstore"
    vectorstore.save_local(str(save_path))
    print(f"    Saved to {save_path}")

    print("\n Ingestion complete! Your data is ready for RAG.")
    print(f"   Vector store saved at: {save_path}")
    print("   You can now start your app and RAG will work automatically.")


if __name__ == "__main__":
    main()
