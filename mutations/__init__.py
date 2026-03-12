"""
Центральный экспорт баз данных мутаций по частям тела.
Каждая часть тела имеет свою базу — ID мутаций НЕ универсальны!
"""
from .body import MUTATIONS as BODY_MUTATIONS
from .head import MUTATIONS as HEAD_MUTATIONS
from .ears import MUTATIONS as EARS_MUTATIONS
from .eyebrows import MUTATIONS as EYEBROWS_MUTATIONS
from .eyes import MUTATIONS as EYES_MUTATIONS
from .legs import MUTATIONS as LEGS_MUTATIONS
from .mouth import MUTATIONS as MOUTH_MUTATIONS
from .tail import MUTATIONS as TAIL_MUTATIONS
from .texture import MUTATIONS as TEXTURE_MUTATIONS

# Словарь баз данных по ключам частей тела
MUTATION_DB_BY_PART = {
    "body": BODY_MUTATIONS,
    "head": HEAD_MUTATIONS,
    "ears": EARS_MUTATIONS,
    "eyebrows": EYEBROWS_MUTATIONS,
    "eyes": EYES_MUTATIONS,
    "legs": LEGS_MUTATIONS,
    "mouth": MOUTH_MUTATIONS,
    "tail": TAIL_MUTATIONS,
    "texture": TEXTURE_MUTATIONS,
}

__all__ = ["MUTATION_DB_BY_PART", "BODY_MUTATIONS", "HEAD_MUTATIONS", "EARS_MUTATIONS",
           "EYEBROWS_MUTATIONS", "EYES_MUTATIONS", "LEGS_MUTATIONS",
           "MOUTH_MUTATIONS", "TAIL_MUTATIONS", "TEXTURE_MUTATIONS"]