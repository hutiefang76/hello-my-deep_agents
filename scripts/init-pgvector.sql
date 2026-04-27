-- ============================================================
-- hello-my-deep_agents · pgvector 初始化脚本
-- 自动在容器首次启动时执行
-- ============================================================

-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 长期记忆表 (Ch4.2.1 用)
CREATE TABLE IF NOT EXISTS long_term_memory (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1024),         -- text-embedding-v3 维度 1024
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_long_term_memory_user_id
    ON long_term_memory(user_id);

CREATE INDEX IF NOT EXISTS idx_long_term_memory_embedding
    ON long_term_memory USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- RAG 文档表 (Ch4.2.3 用)
CREATE TABLE IF NOT EXISTS rag_documents (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(256),
    chunk_id INT,
    content TEXT NOT NULL,
    embedding vector(1024),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rag_documents_source
    ON rag_documents(source);

CREATE INDEX IF NOT EXISTS idx_rag_documents_embedding
    ON rag_documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- 健康检查
SELECT 'pgvector ready' AS status, version() AS pg_version;
