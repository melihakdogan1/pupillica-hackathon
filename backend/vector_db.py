import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import json
from typing import List, Dict, Optional
import logging
from pathlib import Path
import numpy as np

load_dotenv()
logger = logging.getLogger(__name__)

class VectorDatabase:
    """Vector database for medical documents"""
    
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "vector_db"
        self.db_path.mkdir(exist_ok=True)
        
        # ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Collections for different document types
        self.kub_collection = self.client.get_or_create_collection(
            name="kub_documents",
            metadata={"description": "Professional drug information (KUB)"}
        )
        
        self.kt_collection = self.client.get_or_create_collection(
            name="kt_documents", 
            metadata={"description": "Patient drug information (KT)"}
        )
        
        # Sentence transformer for embeddings
        self.embeddings_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
    def add_documents(self, processed_data: List[Dict]):
        """Add processed documents to vector database"""
        logger.info("📊 Belgeler vector database'e ekleniyor...")
        
        kub_texts = []
        kub_metadatas = []
        kub_ids = []
        
        kt_texts = []
        kt_metadatas = []
        kt_ids = []
        
        for doc in processed_data:
            if not doc.get("success", False):
                continue
                
            doc_id = f"{doc['drug_name']}_{doc['document_type']}"
            text = doc.get("cleaned_text", "")
            
            if len(text) < 50:  # Skip very short documents
                continue
                
            metadata = {
                "drug_name": doc["drug_name"],
                "document_type": doc["document_type"],
                "file_name": doc["file_name"],
                "structured_data": json.dumps(doc.get("structured_data", {}))
            }
            
            if doc["document_type"] == "KUB":
                kub_texts.append(text)
                kub_metadatas.append(metadata)
                kub_ids.append(doc_id)
            else:  # KT
                kt_texts.append(text)
                kt_metadatas.append(metadata)
                kt_ids.append(doc_id)
        
        # Add to collections in batches
        if kub_texts:
            logger.info(f"📄 {len(kub_texts)} KUB belgesi ekleniyor...")
            self.kub_collection.add(
                documents=kub_texts,
                metadatas=kub_metadatas,
                ids=kub_ids
            )
            
        if kt_texts:
            logger.info(f"📄 {len(kt_texts)} KT belgesi ekleniyor...")
            self.kt_collection.add(
                documents=kt_texts,
                metadatas=kt_metadatas,
                ids=kt_ids
            )
        
        logger.info("✅ Belgeler vector database'e eklendi!")
        
    def search_similar(self, query: str, doc_type: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """Search for similar documents"""
        results = []
        
        collections_to_search = []
        if doc_type == "KUB":
            collections_to_search = [("KUB", self.kub_collection)]
        elif doc_type == "KT":
            collections_to_search = [("KT", self.kt_collection)]
        else:
            collections_to_search = [("KUB", self.kub_collection), ("KT", self.kt_collection)]
        
        for collection_name, collection in collections_to_search:
            try:
                search_results = collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                
                for i, doc_id in enumerate(search_results["ids"][0]):
                    result = {
                        "id": doc_id,
                        "document": search_results["documents"][0][i],
                        "metadata": search_results["metadatas"][0][i],
                        "distance": search_results["distances"][0][i],
                        "collection": collection_name
                    }
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Search error in {collection_name}: {e}")
        
        # Sort by distance (similarity)
        results.sort(key=lambda x: x["distance"])
        return results[:n_results]
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            kub_count = self.kub_collection.count()
            kt_count = self.kt_collection.count()
            
            return {
                "kub_documents": kub_count,
                "kt_documents": kt_count,
                "total_documents": kub_count + kt_count,
                "status": "healthy"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

# Test function
def test_vector_db():
    """Test vector database functionality"""
    db = VectorDatabase()
    
    # Test search
    results = db.search_similar("paracetamol yan etkiler", n_results=3)
    
    print("🔍 Test Arama Sonuçları:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['metadata']['drug_name']} ({result['collection']})")
        print(f"   Similarity: {1 - result['distance']:.3f}")
        print(f"   Preview: {result['document'][:100]}...")
        print()

if __name__ == "__main__":
    test_vector_db()