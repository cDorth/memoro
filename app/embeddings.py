import faiss

dimension = 384
index = faiss.IndexFlatL2(dimension)
import numpy as np
from db import get_all_embeddings
from ia import generate_embedding

def criar_indice_faiss():
    dados = get_all_embeddings()
    if not dados:
        return None, []

    dimension = 384  # compatível com sentence-transformers
    ids, vetores = zip(*dados)

    # Filtro: apenas vetores válidos com dimensão correta
    vetores_validos = []
    ids_validos = []
    for i, v in zip(ids, vetores):
        if isinstance(v, list) and len(v) == dimension:
            vetores_validos.append(v)
            ids_validos.append(i)
        else:
            print(f"⚠️ Vetor com dimensão inválida ignorado (id={i}): {len(v) if isinstance(v, list) else 'N/A'}")

    if not vetores_validos:
        return None, []

    matriz = np.array(vetores_validos).astype('float32')
    index = faiss.IndexFlatL2(dimension)
    index.add(matriz)
    return index, ids_validos

def buscar_semanticamente(query_text, top_k=5):
    index, ids = criar_indice_faiss()
    if not index:
        return []
    query_vec = np.array([generate_embedding(query_text)]).astype('float32')
    distancias, indices = index.search(query_vec, top_k)
    return [ids[i] for i in indices[0] if i < len(ids)]
