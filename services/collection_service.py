from typing import Dict, Any
from database.db import get_db

async def add_to_collection(user_id: str, char_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adiciona um personagem à coleção do usuário com todos os campos necessários
    
    Args:
        user_id: ID do usuário
        char_data: Dados do personagem do banco de dados
    
    Returns:
        Dicionário com o personagem formatado para a coleção
    """
    db = get_db()
    
    # Modelo padronizado do personagem na coleção
    collection_char = {
        "_id": char_data["_id"],
        "name": char_data["name"],
        "rarity": char_data["rarity"],
        "type": char_data.get("type", "hero"),
        "power_base": char_data.get("power_base", 100),
        "stars": 0,  
        "image": char_data.get("image", ""),
        "universe": char_data.get("universe", ""),
    }
    
    # Adiciona à coleção do usuário
    await db["users"].update_one(
        {"_id": user_id},
        {"$push": {"collection": collection_char}}
    )
    
    return collection_char

async def get_original_character(char_id: str) -> Dict[str, Any]:
    """
    Obtém os dados originais do personagem do banco de dados
    
    Args:
        char_id: ID do personagem
    
    Returns:
        Dicionário com os dados do personagem ou None se não encontrado
    """
    db = get_db()
    return await db["characters"].find_one({"_id": char_id})

async def fix_missing_fields(user_id: str, char_id: str) -> bool:
    """
    Corrige campos faltantes em um personagem da coleção do usuário
    
    Args:
        user_id: ID do usuário
        char_id: ID do personagem
    
    Returns:
        True se a correção foi bem-sucedida, False caso contrário
    """
    db = get_db()
    
    # Obtém o personagem original
    original_char = await get_original_character(char_id)
    if not original_char:
        return False
    
    # Atualiza os campos faltantes
    result = await db["users"].update_one(
        {"_id": user_id, "collection._id": char_id},
        {"$set": {
            "collection.$.type": original_char.get("type", "hero"),
            "collection.$.universe": original_char.get("universe", ""),
        }}
    )
    
    return result.modified_count > 0