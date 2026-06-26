from fastapi import APIRouter, HTTPException, status

from app.api.v1.auth import create_tokens_for_user
from app.core.exceptions import UserNotFoundError
from app.schemas.auth import TokenResponse, VerifyCode, ResendCodeRequest
from app.services import email as verification_service
from app.services import user as user_service
from app.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["Verification"])

@router.post("/verify", response_model=TokenResponse)
async def verify_email(
    data: VerifyCode,
):
    try:
        user = await user_service.get_by_email(str(data.email))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")

    await verification_service.verify_code(code=data.code, user=user)

    access_token, refresh_token = await create_tokens_for_user(user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/resend-code")
async def resend_verification_code(
    data: ResendCodeRequest,
):
    try:
        user = await user_service.get_by_email(str(data.email))
    except UserNotFoundError:
        return {"detail": "Verification code resent"}

    if user.is_verified:
        return {"detail": "Verification code resent"}

    code = await verification_service.generate_verification_code(user)
    await send_verification_email(email_to=user.email, code=code.code)
    return {"detail": "Verification code resent"}