from typing import List, Dict, Any
from src.vectorstore.chroma_store import ChromaStore


class RetrievalOrchestrator:
    """
    检索编排模块
    
    负责协调从向量数据库中检索相关信息。
    支持多种检索策略 (Hot, Valid, Background) 并聚合结果。
    """
    def __init__(self, store: ChromaStore):
        self._store = store

    def aggregate(self, query: str, quotas: Dict[str, int] | None = None) -> List[Dict[str, Any]]:
        """
        聚合检索结果
        
        Args:
            query: 查询文本
            quotas: 各类检索结果的配额字典
            
        Returns:
            List[Dict]: 检索到的文档列表
        """
        quotas = quotas or {"hot": 4, "valid_7d": 4, "background_30d": 2, "background_legacy": 1}
        results = []
        seen = set()
        hot_docs = self._store.similarity_search(query, n_results=quotas.get("hot", 0), where={"hot": True})
        valid_docs = self._store.similarity_search(query, n_results=quotas.get("valid_7d", 0), where={"time_category": "valid_7d"})
        bg30_docs = self._store.similarity_search(query, n_results=quotas.get("background_30d", 0), where={"time_category": "background_30d"})
        legacy_docs = self._store.similarity_search(query, n_results=quotas.get("background_legacy", 0), where={"time_category": "background_legacy"})
        for bucket in [hot_docs, valid_docs, bg30_docs, legacy_docs]:
            for d in bucket:
                if d["id"] in seen:
                    continue
                seen.add(d["id"])
                results.append(d)
        return results
