"""
WhatsApp Share Service for Fake News Detection
Generates formatted messages and share links for WhatsApp
"""

from typing import Dict, Any
from urllib.parse import quote


class WhatsAppShareService:
    """Service to generate WhatsApp share messages and links"""
    
    def __init__(self, brand_name: str = "Sach.ai"):
        """
        Initialize WhatsApp share service
        
        Args:
            brand_name: Name to display in verification message
        """
        self.brand_name = brand_name
    
    def format_message(self, text: str, is_fake: bool, description: str = "") -> str:
        """
        Format verification result as WhatsApp message
        
        Args:
            text: News article text
            is_fake: True if fake, False if real
            description: Explanation/description
            
        Returns:
            Formatted WhatsApp message
        """
        status = "FAKE" if is_fake else "REAL"
        
        # Truncate text if too long (WhatsApp limit)
        max_text_length = 200
        display_text = text[:max_text_length]
        if len(text) > max_text_length:
            display_text += "..."
        
        # Build message with proper formatting
        message = f"""*The news "{display_text}"*

*is {status}.*"""
        
        # Add description if provided
        if description:
            message += f"""

*Description:* {description}"""
        
        # Add brand footer
        message += f"""

*Verified by {self.brand_name}*"""
        
        return message
    
    def generate_share_url(self, text: str, is_fake: bool, 
                          description: str = "", phone_number: str = None) -> str:
        """
        Generate WhatsApp share URL
        
        Args:
            text: News article text
            is_fake: True if fake, False if real
            description: Explanation/description
            phone_number: Optional phone number to send to (with country code)
            
        Returns:
            WhatsApp share URL (wa.me format)
        """
        # Format message
        message = self.format_message(text, is_fake, description)
        
        # URL encode
        encoded_message = quote(message)
        
        # Generate URL
        if phone_number:
            # Send to specific number
            url = f"https://wa.me/{phone_number}?text={encoded_message}"
        else:
            # Open WhatsApp with message (user selects recipient)
            url = f"https://wa.me/?text={encoded_message}"
        
        return url
    
    def create_share_data(self, verification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create WhatsApp share data from verification result
        
        Args:
            verification_result: Dict with text, prediction, confidence, description
            
        Returns:
            Dict with formatted_message, share_url, preview
        """
        # Extract data
        text = verification_result.get("text", "")
        
        # Determine if fake
        prediction = verification_result.get("prediction", "Real News")
        is_fake = "fake" in prediction.lower()
        
        # Get description
        description = verification_result.get("description", "")
        if not description:
            confidence = verification_result.get("confidence", {})
            fake_conf = confidence.get("fake", 0)
            real_conf = confidence.get("real", 0)
            description = f"Confidence: {max(fake_conf, real_conf):.1f}%"
        
        # Generate formatted message
        formatted_message = self.format_message(text, is_fake, description)
        
        # Generate share URL
        share_url = self.generate_share_url(text, is_fake, description)
        
        return {
            "formatted_message": formatted_message,
            "share_url": share_url,
            "is_fake": is_fake,
            "status": "FAKE" if is_fake else "REAL",
            "text_preview": text[:100] + "..." if len(text) > 100 else text
        }


# Singleton instance
whatsapp_service = WhatsAppShareService()


def generate_whatsapp_share(text: str, is_fake: bool, 
                            description: str = "") -> Dict[str, Any]:
    """
    Simple function to generate WhatsApp share data
    
    Args:
        text: News article text
        is_fake: True if fake news, False if real
        description: Explanation
        
    Returns:
        Dict with message, url, status
    """
    formatted_message = whatsapp_service.format_message(text, is_fake, description)
    share_url = whatsapp_service.generate_share_url(text, is_fake, description)
    
    return {
        "formatted_message": formatted_message,
        "share_url": share_url,
        "status": "FAKE" if is_fake else "REAL"
    }


def create_whatsapp_share_from_result(verification_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create WhatsApp share data from complete verification result
    
    Args:
        verification_result: Full verification result dict
        
    Returns:
        WhatsApp share data
    """
    return whatsapp_service.create_share_data(verification_result)

