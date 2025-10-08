"""
AI service for processing delivery note images
"""
import anthropic
import base64
import json
import re
from datetime import datetime
from typing import List, Optional
from io import BytesIO
from PIL import Image
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    HEIF_SUPPORT = False
from ..config import settings
from ..models.schemas import EquipmentMovement, ExtractionResult, EquipmentType, Direction

class AIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def extract_equipment_from_image(self, image_bytes: bytes, driver_name: str = None) -> ExtractionResult:
        """
        Uses Claude Vision API to extract equipment movement data from delivery note photos
        Supports JPEG, PNG, WEBP, GIF, and HEIC (iPhone) formats
        """
        try:
            # Convert HEIC/HEIF to JPEG if needed, or ensure proper format
            try:
                img = Image.open(BytesIO(image_bytes))
                
                # Convert to RGB if needed (handles RGBA, P, L modes)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Re-encode as JPEG for consistent processing
                output = BytesIO()
                img.save(output, format='JPEG', quality=95)
                image_bytes = output.getvalue()
                media_type = "image/jpeg"
                
            except Exception as conversion_error:
                # If conversion fails, try to use original bytes
                print(f"Image conversion warning: {conversion_error}")
                # Determine media type from image bytes
                if image_bytes[:2] == b'\xff\xd8':
                    media_type = "image/jpeg"
                elif image_bytes[:4] == b'\x89PNG':
                    media_type = "image/png"
                elif image_bytes[:4] == b'RIFF':
                    media_type = "image/webp"
                elif image_bytes[:4] == b'GIF8':
                    media_type = "image/gif"
                else:
                    media_type = "image/jpeg"  # fallback
            
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Create prompt for Claude
            prompt = """Analyze this delivery note/paperwork image and extract equipment movement information.

Look for:
1. Customer name or delivery location
2. Equipment types (pallets, cages, dollies, stillages)
3. Quantities of each equipment type
4. Whether equipment is being delivered TO customer (IN) or collected FROM customer (OUT)
5. Date/time if visible
6. Any other relevant notes

Return the information in this exact JSON format:
{
    "customer_name": "string",
    "movements": [
        {
            "equipment_type": "pallet|cage|dolly|stillage|other",
            "quantity": number,
            "direction": "in|out"
        }
    ],
    "date": "YYYY-MM-DD or null",
    "notes": "any additional context",
    "confidence": 0.0-1.0
}

If you cannot extract information confidently, set confidence below 0.7 and explain why in notes."""

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-latest",
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
                                    "data": base64_image,
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
            
            # Parse Claude's response
            response_text = message.content[0].text
            
            # Extract JSON from response (Claude might wrap it in markdown)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse JSON from response")
            
            # Convert to EquipmentMovement objects
            movements = []
            for movement_data in extracted_data.get("movements", []):
                movement = EquipmentMovement(
                    movement_id=f"mov_{datetime.now().timestamp()}_{len(movements)}",
                    customer_name=extracted_data["customer_name"],
                    equipment_type=EquipmentType(movement_data["equipment_type"]),
                    quantity=movement_data["quantity"],
                    direction=Direction(movement_data["direction"]),
                    timestamp=datetime.now(),
                    driver_name=driver_name,
                    confidence_score=extracted_data.get("confidence", 0.5),
                    notes=extracted_data.get("notes"),
                    verified=False
                )
                movements.append(movement)
            
            return ExtractionResult(
                success=True,
                movements=movements,
                raw_text=response_text
            )
            
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error messages
            if "Could not process image" in error_msg or "invalid_request_error" in error_msg:
                user_friendly_msg = "The image could not be processed by AI. Please ensure you're uploading a clear, readable delivery note photo (not a tiny test image). The image should be at least 200x200 pixels with visible text content."
            else:
                user_friendly_msg = f"AI processing error: {error_msg}"
            
            return ExtractionResult(
                success=False,
                movements=[],
                error=user_friendly_msg,
                raw_text=error_msg
            )

# Global instance
ai_service = AIService()

