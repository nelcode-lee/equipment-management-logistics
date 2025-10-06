"""
AI service for processing delivery note images
"""
import anthropic
import base64
import json
import re
from datetime import datetime
from typing import List, Optional
from ..config import settings
from ..models.schemas import EquipmentMovement, ExtractionResult, EquipmentType, Direction

class AIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def extract_equipment_from_image(self, image_bytes: bytes, driver_name: str = None) -> ExtractionResult:
        """
        Uses Claude Vision API to extract equipment movement data from delivery note photos
        """
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Determine media type (simplified - assumes JPEG)
            media_type = "image/jpeg"
            
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
                model="claude-3-5-sonnet-20241022",
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
            return ExtractionResult(
                success=False,
                movements=[],
                error=str(e)
            )

# Global instance
ai_service = AIService()

