"""
Vector store interface and ChromaDB implementation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import uuid

from app.core.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector store."""
        pass
    
    @abstractmethod
    async def add_document(
        self,
        document: str,
        metadata: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> str:
        """Add a document to the vector store."""
        pass
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add multiple documents to the vector store."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Delete a document from the vector store."""
        pass
    
    @abstractmethod
    async def get(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the vector store connection."""
        pass


class ChromaVectorStore(VectorStore):
    """ChromaDB implementation of VectorStore."""
    
    def __init__(self, collection_name: Optional[str] = None):
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.client = None
        self.collection = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Initialize ChromaDB with persistence
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            self._initialized = True
            logger.info("ChromaDB initialized", collection=self.collection_name)
            
        except Exception as e:
            logger.error("Failed to initialize ChromaDB", error=str(e))
            raise
    
    async def add_document(
        self,
        document: str,
        metadata: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> str:
        """Add a single document to the vector store."""
        if not self._initialized:
            await self.initialize()
        
        doc_id = document_id or str(uuid.uuid4())
        
        try:
            self.collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.debug("Document added to vector store", document_id=doc_id)
            return doc_id
            
        except Exception as e:
            logger.error("Failed to add document", document_id=doc_id, error=str(e))
            raise
    
    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add multiple documents to the vector store."""
        if not self._initialized:
            await self.initialize()
        
        if len(documents) != len(metadatas):
            raise ValueError("Documents and metadatas must have the same length")
        
        doc_ids = ids or [str(uuid.uuid4()) for _ in documents]
        
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=doc_ids
            )
            logger.debug("Documents added to vector store", count=len(documents))
            return doc_ids
            
        except Exception as e:
            logger.error("Failed to add documents", error=str(e))
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using semantic search."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Adjust top_k if collection is smaller
            actual_top_k = min(top_k, self.collection.count())
            
            results = self.collection.query(
                query_texts=[query],
                n_results=actual_top_k,
                where=filters,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None,
                    })
            
            logger.debug("Vector search completed", results_count=len(formatted_results))
            return formatted_results
            
        except Exception as e:
            logger.error("Vector search failed", error=str(e))
            return []
    
    async def delete(self, document_id: str) -> bool:
        """Delete a document from the vector store."""
        if not self._initialized:
            await self.initialize()
        
        try:
            self.collection.delete(ids=[document_id])
            logger.debug("Document deleted from vector store", document_id=document_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete document", document_id=document_id, error=str(e))
            return False
    
    async def get(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        if not self._initialized:
            await self.initialize()
        
        try:
            results = self.collection.get(
                ids=[document_id],
                include=["documents", "metadatas"]
            )
            
            if results["documents"] and results["documents"][0]:
                return {
                    "id": document_id,
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {},
                }
            
            return None
            
        except Exception as e:
            logger.error("Failed to get document", document_id=document_id, error=str(e))
            return None
    
    async def close(self) -> None:
        """Close the vector store connection."""
        self.client = None
        self.collection = None
        self._initialized = False
        logger.info("ChromaDB connection closed")
