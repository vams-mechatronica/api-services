import uuid

class GenerateUUID:

    @staticmethod
    def generate_unique_username():
        return f"user_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def generate_random_email():
        return f"user_{uuid.uuid4().hex[:8]}@example.com"
    
    @staticmethod
    def generate_whatsapp_otp_message_id():
        return str(uuid.uuid1())
    
    @staticmethod
    def generate_sku(prefix='SKU'):
        return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"