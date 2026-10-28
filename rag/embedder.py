import logging
import os

# На Streamlit Cloud нет GPU. Переменная должна стоять до первого импорта torch,
# поэтому сам torch импортируется ниже, внутри load_model
os.environ["CUDA_VISIBLE_DEVICES"] = ""

logger = logging.getLogger(__name__)

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def load_model():
    """Модель эмбеддингов или None, если torch / sentence-transformers нет или модель не скачалась."""
    try:
        import torch
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.warning("sentence-transformers is not installed, falling back to TF-IDF")
        return None

    # лишние потоки только съедают память
    torch.set_num_threads(1)
    try:
        return SentenceTransformer(MODEL_NAME, device="cpu")
    except Exception:
        logger.exception("Failed to load embedding model %s", MODEL_NAME)
        return None


def encode(model, texts):
    """Нормированные векторы: косинусное сходство сводится к скалярному произведению."""
    return model.encode(list(texts), normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
