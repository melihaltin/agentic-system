from supabase import Client
from features.businesses.models import BusinessCreate, BusinessUpdate
from typing import Optional, Dict, Any
from uuid import UUID
import structlog

logger = structlog.get_logger()


class BusinessRepository:
    """Repository for Business operations using Supabase."""
    
    def __init__(self, client: Client):
        self.client = client
        self.table_name = 'businesses'
    
    async def create_business(self, business_data: BusinessCreate, auth_user_id: str) -> Dict[str, Any]:
        """Create a new business."""
        try:
            data = {
                "email": business_data.email,
                "business_type": business_data.business_type,
                "business_name": business_data.business_name,
                "business_website": business_data.business_website,
                "business_phone_number": business_data.business_phone_number,
                "auth_user_id": auth_user_id
            }
            
            response = self.client.table(self.table_name).insert(data).execute()
            
            if response.data:
                logger.info(f"Business created: {business_data.business_name}")
                return response.data[0]
            else:
                raise ValueError("Failed to create business")
                
        except Exception as e:
            logger.error(f"Error creating business: {str(e)}")
            raise ValueError(f"Failed to create business: {str(e)}")
    
    async def get_business_by_id(self, business_id: UUID) -> Optional[Dict[str, Any]]:
        """Get business by ID."""
        try:
            response = self.client.table(self.table_name).select('*').eq('id', str(business_id)).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching business by ID: {str(e)}")
            return None
    
    async def get_business_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get business by email."""
        try:
            response = self.client.table(self.table_name).select('*').eq('email', email).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching business by email: {str(e)}")
            return None
    
    async def get_business_by_auth_user_id(self, auth_user_id: str) -> Optional[Dict[str, Any]]:
        """Get business by Supabase auth user ID."""
        try:
            response = self.client.table(self.table_name).select('*').eq('auth_user_id', auth_user_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching business by auth user ID: {str(e)}")
            return None
    
    async def get_businesses(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get paginated list of businesses."""
        try:
            offset = (page - 1) * per_page
            
            # Get total count
            count_response = self.client.table(self.table_name).select('id', count='exact').execute()
            total = count_response.count if count_response.count else 0
            
            # Get paginated data
            response = self.client.table(self.table_name).select('*').range(offset, offset + per_page - 1).order('created_at', desc=True).execute()
            
            return {
                'businesses': response.data or [],
                'total': total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Error fetching businesses: {str(e)}")
            raise ValueError(f"Failed to fetch businesses: {str(e)}")
    
    async def update_business(self, business_id: UUID, business_data: BusinessUpdate) -> Optional[Dict[str, Any]]:
        """Update business."""
        try:
            update_data = {}
            if business_data.business_name is not None:
                update_data["business_name"] = business_data.business_name
            if business_data.business_website is not None:
                update_data["business_website"] = business_data.business_website
            if business_data.business_phone_number is not None:
                update_data["business_phone_number"] = business_data.business_phone_number
            
            if not update_data:
                raise ValueError("No data to update")
            
            response = self.client.table(self.table_name).update(update_data).eq('id', str(business_id)).execute()
            
            if response.data:
                logger.info(f"Business updated: {business_id}")
                return response.data[0]
            return None
                
        except Exception as e:
            logger.error(f"Error updating business: {str(e)}")
            raise ValueError(f"Failed to update business: {str(e)}")
    
    async def delete_business(self, business_id: UUID) -> bool:
        """Delete business."""
        try:
            response = self.client.table(self.table_name).delete().eq('id', str(business_id)).execute()
            
            if response.data:
                logger.info(f"Business deleted: {business_id}")
                return True
            return False
                
        except Exception as e:
            logger.error(f"Error deleting business: {str(e)}")
            raise ValueError(f"Failed to delete business: {str(e)}")