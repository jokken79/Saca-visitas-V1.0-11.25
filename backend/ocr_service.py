# ============================================================
# UNS VISA SYSTEM - OCR Service
# Extrae datos de 在留カード y パスポート usando Claude Vision
# ============================================================

import anthropic
import base64
import os
import re
from typing import Optional, Dict, Any
from datetime import datetime

# Inicializar cliente Anthropic
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY", "")
)

class OCRService:
    """Servicio de OCR para documentos de inmigración japonesa"""

    ZAIRYU_CARD_PROMPT = """Analiza esta imagen de una 在留カード (Residence Card) japonesa y extrae los siguientes datos en formato JSON:

{
    "residence_card_number": "número de tarjeta (formato: AA00000000BB)",
    "family_name": "apellido en romaji (MAYÚSCULAS)",
    "given_name": "nombre en romaji (MAYÚSCULAS)",
    "family_name_kanji": "apellido en kanji/katakana si visible",
    "given_name_kanji": "nombre en kanji/katakana si visible",
    "nationality": "nacionalidad en japonés (例: ベトナム, 中国, フィリピン)",
    "date_of_birth": "fecha de nacimiento formato YYYY-MM-DD",
    "sex": "male o female",
    "current_visa_status": "在留資格 (例: 技術・人文知識・国際業務)",
    "current_period_of_stay": "在留期間 (例: 3年, 1年)",
    "current_expiration_date": "在留期限 formato YYYY-MM-DD",
    "address_japan": "住所 si es visible"
}

IMPORTANTE:
- Solo incluye campos que puedas leer claramente
- Si no puedes leer un campo, omítelo del JSON
- Fechas en formato YYYY-MM-DD
- Nombres en MAYÚSCULAS para romaji
- Devuelve SOLO el JSON, sin explicaciones"""

    PASSPORT_PROMPT = """Analiza esta imagen de un パスポート (Passport) y extrae los siguientes datos en formato JSON:

{
    "passport_number": "número de pasaporte",
    "family_name": "apellido en romaji (MAYÚSCULAS)",
    "given_name": "nombre en romaji (MAYÚSCULAS)",
    "nationality": "nacionalidad en japonés (例: ベトナム, 中国, フィリピン)",
    "date_of_birth": "fecha de nacimiento formato YYYY-MM-DD",
    "sex": "male o female",
    "passport_expiration": "fecha de expiración formato YYYY-MM-DD",
    "passport_issue_country": "país de emisión",
    "place_of_birth": "lugar de nacimiento"
}

IMPORTANTE:
- Solo incluye campos que puedas leer claramente
- Si no puedes leer un campo, omítelo del JSON
- Fechas en formato YYYY-MM-DD
- Nombres en MAYÚSCULAS
- Devuelve SOLO el JSON, sin explicaciones"""

    @staticmethod
    def extract_from_image(image_base64: str, document_type: str) -> Dict[str, Any]:
        """
        Extrae datos de una imagen usando Claude Vision

        Args:
            image_base64: Imagen en base64 (sin el prefijo data:image/...)
            document_type: "zairyu_card" o "passport"

        Returns:
            Diccionario con los datos extraídos
        """
        # Determinar el prompt según el tipo de documento
        if document_type == "zairyu_card":
            prompt = OCRService.ZAIRYU_CARD_PROMPT
        elif document_type == "passport":
            prompt = OCRService.PASSPORT_PROMPT
        else:
            raise ValueError(f"Tipo de documento no soportado: {document_type}")

        # Detectar tipo de imagen
        media_type = "image/jpeg"
        if image_base64.startswith("/9j/"):
            media_type = "image/jpeg"
        elif image_base64.startswith("iVBOR"):
            media_type = "image/png"
        elif image_base64.startswith("R0lGOD"):
            media_type = "image/gif"

        try:
            # Llamar a Claude Vision
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # Parsear respuesta JSON
            response_text = message.content[0].text

            # Limpiar la respuesta (quitar markdown si existe)
            json_text = response_text.strip()
            if json_text.startswith("```"):
                json_text = re.sub(r'^```json?\s*', '', json_text)
                json_text = re.sub(r'\s*```$', '', json_text)

            import json
            extracted_data = json.loads(json_text)

            # Convertir nacionalidad a formato japonés si es necesario
            nationality_map = {
                "Vietnam": "ベトナム",
                "VIETNAM": "ベトナム",
                "Vietnamese": "ベトナム",
                "China": "中国",
                "CHINA": "中国",
                "Chinese": "中国",
                "Philippines": "フィリピン",
                "PHILIPPINES": "フィリピン",
                "Filipino": "フィリピン",
                "Indonesia": "インドネシア",
                "INDONESIA": "インドネシア",
                "Indonesian": "インドネシア",
                "Nepal": "ネパール",
                "NEPAL": "ネパール",
                "Nepalese": "ネパール",
                "Brazil": "ブラジル",
                "BRAZIL": "ブラジル",
                "Brazilian": "ブラジル",
            }

            if "nationality" in extracted_data:
                nat = extracted_data["nationality"]
                extracted_data["nationality"] = nationality_map.get(nat, nat)

            return {
                "success": True,
                "document_type": document_type,
                "extracted_data": extracted_data,
                "confidence": "high"  # Claude es bastante preciso
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Error parseando respuesta JSON: {str(e)}",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except anthropic.APIError as e:
            return {
                "success": False,
                "error": f"Error de API Anthropic: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error inesperado: {str(e)}"
            }

    @staticmethod
    def get_missing_fields(employee_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Identifica qué campos importantes están vacíos

        Args:
            employee_data: Datos actuales del empleado

        Returns:
            Diccionario con campos y si están vacíos (True = falta)
        """
        important_fields = {
            # Datos personales
            "family_name": "姓 (ローマ字)",
            "given_name": "名 (ローマ字)",
            "family_name_kanji": "姓 (漢字)",
            "given_name_kanji": "名 (漢字)",
            "nationality": "国籍",
            "date_of_birth": "生年月日",
            "sex": "性別",

            # Pasaporte
            "passport_number": "旅券番号",
            "passport_expiration": "旅券有効期限",

            # Visa
            "current_visa_status": "在留資格",
            "current_period_of_stay": "在留期間",
            "current_expiration_date": "在留期限",
            "residence_card_number": "在留カード番号",

            # Contacto
            "address_japan": "住所",
            "cellular_phone": "携帯電話",
        }

        missing = {}
        for field, label in important_fields.items():
            value = employee_data.get(field)
            is_missing = value is None or value == "" or value == "null"
            missing[field] = {
                "label": label,
                "is_missing": is_missing,
                "current_value": value if not is_missing else None
            }

        return missing

    @staticmethod
    def merge_ocr_data(existing_data: Dict[str, Any], ocr_data: Dict[str, Any], only_fill_missing: bool = True) -> Dict[str, Any]:
        """
        Combina datos existentes con datos OCR

        Args:
            existing_data: Datos actuales del empleado
            ocr_data: Datos extraídos por OCR
            only_fill_missing: Si True, solo llena campos vacíos

        Returns:
            Datos combinados
        """
        result = existing_data.copy()

        for field, value in ocr_data.items():
            if value is None or value == "":
                continue

            if only_fill_missing:
                # Solo llenar si está vacío
                existing_value = existing_data.get(field)
                if existing_value is None or existing_value == "" or existing_value == "null":
                    result[field] = value
            else:
                # Sobrescribir siempre
                result[field] = value

        return result
