import secrets

import aiosmtplib
from pydantic import EmailStr
from app.core.config import settings
from email.message import EmailMessage

from app.core.exceptions import InvalidVerificationCode
from app.models.user import User
from app.models.verification_code import VerificationCode


async def generate_verification_code(user: User) -> VerificationCode:
    old_codes = await VerificationCode.find(
        VerificationCode.user.id == user.id
    ).to_list()
    for old in old_codes:
        await old.delete()

    code_int = 100000 + secrets.randbelow(900000)
    code = VerificationCode(
        code=code_int,
        user=user  # type: ignore[arg-type]
    )
    await code.insert()
    return code

async def verify_code(
        code: int,
        user: User
) -> bool:
    verification = await VerificationCode.find_one(
        VerificationCode.code == code,
        VerificationCode.user.id == user.id
    )
    if verification:
        user.is_verified = True
        await user.save()

        await verification.delete()
        return True
    raise InvalidVerificationCode()

async def send_email(
        to: EmailStr,
        subject: str,
        html_content: str,
        text: str | None = None
) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_EMAIL_FROM
    msg["To"] = to
    msg.set_content(text or "Please use an HTML compatible email client to view")
    msg.add_alternative(html_content, subtype="html")

    async with aiosmtplib.SMTP(
            hostname = settings.EMAIL_SMTP_SERVER,
            port = settings.EMAIL_SMTP_PORT,
            start_tls = True,
    ) as smtp:
        await smtp.login(settings.EMAIL_SMTP_USERNAME, settings.EMAIL_SMTP_PASSWORD)
        await smtp.send_message(msg)


async def send_verification_email(
        email_to: EmailStr,
        code: int
) -> None:
    subject = "Подтверждение email"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
            <tr>
                <td style="padding: 40px 30px; text-align: center; background-color: #4F46E5;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Подтверждение почты</h1>
                </td>
            </tr>
            <tr>
                <td style="padding: 40px 30px;">
                    <p style="font-size: 16px; color: #333333; margin-bottom: 20px;">Здравствуйте!</p>
                    <p style="font-size: 16px; color: #333333; margin-bottom: 30px;">
                        Спасибо за регистрацию. Чтобы подтвердить ваш email, используйте следующий код:
                    </p>

                    <div style="background-color: #f8f9fa; border-radius: 8px; padding: 30px; text-align: center; margin-bottom: 30px;">
                        <span style="font-size: 32px; font-weight: bold; color: #4F46E5; letter-spacing: 8px;">{code}</span>
                    </div>

                    <p style="font-size: 14px; color: #666666; margin-bottom: 20px;">
                        Код действителен в течение 10 минут. Если вы не запрашивали этот код, просто проигнорируйте письмо.
                    </p>

                    <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">

                    <p style="font-size: 12px; color: #999999; text-align: center;">
                        Это автоматическое письмо. Пожалуйста, не отвечайте на него.
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    text = f"""Подтверждение email

Здравствуйте!

Спасибо за регистрацию. Чтобы подтвердить ваш email, используйте следующий код:

{code}

Код действителен в течение 10 минут. Если вы не запрашивали этот код, просто проигнорируйте письмо.

Это автоматическое письмо. Пожалуйста, не отвечайте на него."""

    await send_email(
        to=email_to,
        subject=subject,
        html_content=html_content,
        text=text
    )