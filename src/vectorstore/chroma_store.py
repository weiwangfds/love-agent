from typing import List, Dict, Any
import os
import chromadb
from chromadb.config import Settings


class ChromaStore:
    """
    ChromaDB 向量数据库封装
    
    负责文本数据的向量化存储和检索。
    """
    def __init__(self, persist_directory: str, collection_name: str):
        """
        初始化向量数据库
        
        Args:
            persist_directory: 数据持久化目录
            collection_name: 集合名称
        """
        self._client = chromadb.Client(Settings(persist_directory=persist_directory, allow_reset=True))
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def add_texts(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]):
        """
        添加文本到向量库
        """
        self._collection.add(ids=ids, documents=texts, metadatas=metadatas)

    def has_id(self, id: str) -> bool:
        """
        检查指定 ID 是否已存在
        """
        res = self._collection.get(ids=[id])
        return bool(res.get("ids"))

    def add_text_if_not_exists(self, id: str, text: str, metadata: Dict[str, Any]):
        """
        如果 ID 不存在则添加文本（用于去重）
        """
        if not self.has_id(id):
            self._collection.add(ids=[id], documents=[text], metadatas=[metadata])

    def similarity_search(self, query: str, n_results: int = 5, where: Dict[str, Any] | None = None):
        """
        执行相似度搜索
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 过滤条件 (Metadata 过滤)
            
        Returns:
            List[Dict]: 包含 id, text, metadata, distance 的结果列表
        """
        # 处理空 where 子句，如果是空字典则传入 None
        query_where = where if where else None
        res = self._collection.query(query_texts=[query], n_results=n_results, where=query_where)
        docs = []
        for i in range(len(res["documents"][0])):
            docs.append(
                {
                    "id": res["ids"][0][i],
                    "text": res["documents"][0][i],
                    "metadata": res["metadatas"][0][i],
                    "distance": res.get("distances", [[None]])[0][i],
                }
            )
        return docs
