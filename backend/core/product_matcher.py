import logging
import os
from typing import List, Tuple, Optional
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from core.models import Persona, Product

logger = logging.getLogger(__name__)


class ProductMatcher:
    """
    Matches users to appropriate products based on their persona.
    Uses RAG with FAISS and Hugging Face Embeddings (local/free).
    """

    def __init__(self, products: List[Product], api_key: Optional[str] = None):
        self.products = products
        self.product_map = {p.id: p for p in products}
        self.retriever = None

        if not products:
            logger.warning("ProductMatcher initialized with empty product list")
            return

        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as e:
            logger.error("Failed to initialize HuggingFace embeddings: %s", str(e))
            return

        try:
            docs = []
            for p in products:
                content = (
                    f"Name: {p.name}\n"
                    f"Description: {p.description}\n"
                    f"Benefit: {p.core_benefit}\n"
                    f"Audience: {', '.join(p.target_audience)}\n"
                    f"Categories: {', '.join(p.categories)}\n"
                    f"Keywords: {', '.join(p.trigger_keywords or [])}"
                )
                docs.append(Document(page_content=content, metadata={"id": p.id}))

            self.vector_store = FAISS.from_documents(docs, self.embeddings)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})
            logger.info("ProductMatcher initialized with %d products", len(products))
        except Exception as e:
            logger.error("Failed to build FAISS vector store: %s", str(e))
            self.retriever = None

    def match(self, persona: Persona) -> List[Product]:
        """Find products that best match the user's persona."""
        if not self.retriever or not self.products:
            logger.warning("Retriever not available, returning empty matches")
            return []

        try:
            persona_parts = [
                persona.professional_background,
                persona.financial_goals,
                persona.learning_goals,
                persona.career_stage,
                persona.transition_intent,
                " ".join(persona.interests or [])
            ]
            persona_text = " ".join(filter(None, persona_parts)).strip()

            if not persona_text:
                logger.info("No persona data available, using broadest product fallback")
                return [self._get_broadest_product()]

            docs = self.retriever.invoke(persona_text)
            matched_products = []
            for d in docs:
                pid = d.metadata.get("id")
                if pid in self.product_map:
                    matched_products.append(self.product_map[pid])

            logger.info("Matched %d products for persona", len(matched_products))
            return matched_products

        except Exception as e:
            logger.error("Product matching failed: %s", str(e))
            return []

    def calculate_relevance_score(self, persona: Persona, product: Product) -> float:
        """Helper for legacy compatibility."""
        try:
            return 1.0 if product in self.match(persona) else 0.0
        except Exception:
            return 0.0

    def _get_broadest_product(self) -> Product:
        """Fallback: Find product with broadest target audience."""
        if not self.products:
            raise ValueError("No products available")
        return max(self.products, key=lambda p: len(p.target_audience))

    def get_top_n_products(self, persona: Persona, n: int = 5) -> List[Tuple[Product, float]]:
        """Get top N products for the persona with dummy scores."""
        try:
            matches = self.match(persona)
            return [(p, 1.0) for p in matches][:n]
        except Exception as e:
            logger.error("get_top_n_products failed: %s", str(e))
            return []
