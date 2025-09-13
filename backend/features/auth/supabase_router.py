from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from features.businesses.models import BusinessCreate, BusinessResponse, BusinessAuthResponse
from core.supabase import get_supabase_client, get_supabase_service_client
from core.config import settings
import structlog
from uuid import uuid4

logger = structlog.get_logger()
router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def get_supabase():
    """Get Supabase client."""
    return get_supabase_client()


def get_supabase_service():
    """Get Supabase service client for admin operations."""
    return get_supabase_service_client()


@router.post("/register", response_model=BusinessAuthResponse, status_code=status.HTTP_201_CREATED)
async def register_business(
    business_data: BusinessCreate,
    supabase=Depends(get_supabase),
    service_client=Depends(get_supabase_service)
):
    """Register a new business with Supabase Auth."""
    try:
        logger.info(f"Starting business registration for email: {business_data.email}")
        
        # 1. Register user with Supabase Auth
        try:
            auth_response = supabase.auth.sign_up({
                "email": business_data.email,
                "password": business_data.password,
                "options": {
                    "data": {
                        "business_name": business_data.business_name,
                        "business_type": business_data.business_type
                    }
                }
            })
            logger.info(f"Supabase auth signup completed for: {business_data.email}")
        except Exception as e:
            logger.error(f"Supabase auth signup failed for {business_data.email}: {str(e)}")
            # Check if user already exists
            if "User already registered" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication service error: {str(e)}"
            )
        
        if auth_response.user is None:
            logger.error(f"Auth response user is None for: {business_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )
        
        user = auth_response.user
        session = auth_response.session
        logger.info(f"User created successfully with ID: {user.id}")
        
        # 2. Create business record in database using service client
        business_record = {
            "id": str(uuid4()),
            "email": business_data.email,
            "business_type": business_data.business_type,
            "business_name": business_data.business_name,
            "business_website": business_data.business_website,
            "business_phone_number": business_data.business_phone_number,
            "auth_user_id": user.id
        }
        
        try:
            db_response = service_client.table("businesses").insert(business_record).execute()
            logger.info(f"Database insert attempted for business: {business_data.business_name}")
        except Exception as e:
            logger.error(f"Database insert failed for {business_data.email}: {str(e)}")
            # Rollback: delete the auth user if business creation fails
            try:
                service_client.auth.admin.delete_user(user.id)
                logger.info(f"Rolled back auth user: {user.id}")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {str(rollback_error)}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create business record: {str(e)}"
            )
        
        if not db_response.data:
            logger.error(f"Database response has no data for: {business_data.email}")
            # Rollback: delete the auth user if business creation fails
            try:
                service_client.auth.admin.delete_user(user.id)
                logger.info(f"Rolled back auth user: {user.id}")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {str(rollback_error)}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create business record - no data returned"
            )
        
        business = db_response.data[0]
        logger.info(f"Business registered successfully: {business_data.email}")
        
        return BusinessAuthResponse(
            business=BusinessResponse(**business),
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            expires_in=session.expires_in,
            token_type="bearer"
        )
        
    except HTTPException as he:
        # Re-raise HTTPExceptions (they are already handled properly)
        logger.error(f"HTTP exception during registration: {he.detail}")
        raise he
    except Exception as e:
        # Catch any unexpected exceptions
        logger.error(f"Unexpected error during business registration for {business_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )


@router.post("/login", response_model=BusinessAuthResponse)
async def login_business(
    login_data: LoginRequest,
    supabase=Depends(get_supabase)
):
    """Login business with Supabase Auth."""
    try:
        logger.info(f"Starting business login for email: {login_data.email}")
        
        # 1. Authenticate with Supabase
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": login_data.email,
                "password": login_data.password
            })
            logger.info(f"Supabase auth signin completed for: {login_data.email}")
        except Exception as e:
            logger.error(f"Supabase auth signin failed for {login_data.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if auth_response.user is None:
            logger.error(f"Auth response user is None for: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = auth_response.user
        session = auth_response.session
        logger.info(f"User authenticated successfully with ID: {user.id}")
        
        # 2. Get business record
        try:
            business_response = supabase.table("businesses").select("*").eq("email", login_data.email).single().execute()
            logger.info(f"Business data query completed for: {login_data.email}")
        except Exception as e:
            logger.error(f"Business data query failed for {login_data.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business record not found"
            )
        
        if not business_response.data:
            logger.error(f"Business data not found for: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        business = business_response.data
        logger.info(f"Business logged in successfully: {login_data.email}")
        
        return BusinessAuthResponse(
            business=BusinessResponse(**business),
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            expires_in=session.expires_in,
            token_type="bearer"
        )
        
    except HTTPException as he:
        # Re-raise HTTPExceptions (they are already handled properly)
        logger.error(f"HTTP exception during login: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during business login for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="An unexpected error occurred during login"
        )


@router.post("/logout")
async def logout_business(supabase=Depends(get_supabase)):
    """Logout business from Supabase Auth."""
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return {"message": "Logged out"}