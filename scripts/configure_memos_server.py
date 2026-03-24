#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path

COGNEE_COMPOSE = Path('/Users/scott/.openclaw/cognee/docker-compose.yml')
COGNEE_ENV = Path('/Users/scott/.openclaw/cognee/.env')
SERVICE_DIR = Path('/Users/scott/.openclaw/services/memos-server')
ENV_PATH = SERVICE_DIR / '.env'


def extract_yaml_value(text: str, key: str) -> str | None:
    m = re.search(rf'^[ \t]*{re.escape(key)}:[ \t]*(.+?)\s*$', text, re.M)
    if not m:
        return None
    value = m.group(1).strip()
    if value.startswith(('"', "'")) and value.endswith(('"', "'")):
        value = value[1:-1]
    return value


def load_env_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        result[k.strip()] = v.strip()
    return result


def resolve(value: str | None, env_vars: dict[str, str]) -> str | None:
    if not value:
        return value
    # expand simple ${VAR} references
    for k, v in env_vars.items():
        value = value.replace(f'${{{k}}}', v)
    return value if not value.startswith('${') else None


def main() -> int:
    SERVICE_DIR.mkdir(parents=True, exist_ok=True)
    if not COGNEE_COMPOSE.exists():
        raise SystemExit(f'Missing source config: {COGNEE_COMPOSE}')

    cognee_env = load_env_file(COGNEE_ENV)
    compose_text = COGNEE_COMPOSE.read_text()

    llm_model_raw = extract_yaml_value(compose_text, 'LLM_MODEL') or 'Qwen/Qwen2.5-72B-Instruct'
    llm_model = resolve(llm_model_raw, cognee_env) or llm_model_raw
    llm_endpoint = resolve(extract_yaml_value(compose_text, 'LLM_ENDPOINT'), cognee_env) or 'https://api.siliconflow.cn/v1'
    llm_api_key = resolve(extract_yaml_value(compose_text, 'LLM_API_KEY'), cognee_env) or cognee_env.get('SILICONFLOW_API_KEY') or cognee_env.get('LLM_API_KEY')

    embedding_model_raw = extract_yaml_value(compose_text, 'EMBEDDING_MODEL') or 'BAAI/bge-m3'
    embedding_model = resolve(embedding_model_raw, cognee_env) or embedding_model_raw
    embedding_endpoint = resolve(extract_yaml_value(compose_text, 'EMBEDDING_ENDPOINT'), cognee_env) or llm_endpoint
    embedding_api_key = resolve(extract_yaml_value(compose_text, 'EMBEDDING_API_KEY'), cognee_env) or cognee_env.get('SILICONFLOW_API_KEY') or cognee_env.get('EMBEDDING_API_KEY') or llm_api_key
    embedding_dimensions = resolve(extract_yaml_value(compose_text, 'EMBEDDING_DIMENSIONS'), cognee_env) or '1024'

    if not llm_api_key:
        raise SystemExit('LLM_API_KEY not found; cannot bootstrap MemOS securely.')
    if not embedding_api_key:
        raise SystemExit('EMBEDDING_API_KEY not found; cannot bootstrap MemOS securely.')

    env = {
        'TZ': 'Asia/Shanghai',
        'MOS_CUBE_PATH': str(SERVICE_DIR / 'data'),
        'MEMOS_BASE_PATH': str(SERVICE_DIR),
        'MOS_ENABLE_DEFAULT_CUBE_CONFIG': 'true',
        'MOS_ENABLE_REORGANIZE': 'false',
        'MOS_TEXT_MEM_TYPE': 'general_text',
        'ASYNC_MODE': 'sync',
        'MOS_TOP_K': '20',
        'MOS_CHAT_MODEL_PROVIDER': 'openai',
        'MOS_CHAT_MODEL': llm_model.replace('openai/', ''),
        'MOS_CHAT_TEMPERATURE': '0.2',
        'MOS_MAX_TOKENS': '4096',
        'MOS_TOP_P': '0.9',
        'OPENAI_API_KEY': llm_api_key,
        'OPENAI_API_BASE': llm_endpoint,
        'MEMRADER_MODEL': llm_model.replace('openai/', ''),
        'MEMRADER_API_KEY': llm_api_key,
        'MEMRADER_API_BASE': llm_endpoint,
        'MEMRADER_MAX_TOKENS': '4096',
        'EMBEDDING_DIMENSION': embedding_dimensions,
        'MOS_EMBEDDER_BACKEND': 'universal_api',
        'MOS_EMBEDDER_PROVIDER': 'openai',
        'MOS_EMBEDDER_MODEL': embedding_model.replace('openai/', ''),
        'MOS_EMBEDDER_API_BASE': embedding_endpoint,
        'MOS_EMBEDDER_API_KEY': embedding_api_key,
        'MOS_RERANKER_BACKEND': 'cosine_local',
        'ENABLE_INTERNET': 'false',
        'ENABLE_PREFERENCE_MEMORY': 'true',
        'MEM_READER_BACKEND': 'simple_struct',
        'MEM_READER_CHAT_CHUNK_TYPE': 'default',
        'MEM_READER_CHAT_CHUNK_TOKEN_SIZE': '1600',
        'MEM_READER_CHAT_CHUNK_SESS_SIZE': '10',
        'MEM_READER_CHAT_CHUNK_OVERLAP': '2',
        'MOS_ENABLE_SCHEDULER': 'false',
        'API_SCHEDULER_ON': 'false',
        'NEO4J_BACKEND': 'neo4j-community',
        'NEO4J_URI': 'bolt://memos-neo4j:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': '12345678',
        'NEO4J_DB_NAME': 'neo4j',
        'MOS_NEO4J_SHARED_DB': 'false',
        'QDRANT_HOST': 'memos-qdrant',
        'QDRANT_PORT': '6333',
        'QDRANT_URL': '',
        'QDRANT_API_KEY': '',
        'AUTH_ENABLED': 'false',
    }

    lines = [f'{k}={v}' for k, v in env.items()]
    ENV_PATH.write_text('\n'.join(lines) + '\n')
    os.chmod(ENV_PATH, 0o600)
    print(f'Wrote {ENV_PATH}')
    print('Configured models/endpoints from existing Cognee SiliconFlow settings.')
    print('API key values were written without printing them.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
