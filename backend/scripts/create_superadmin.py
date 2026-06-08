import beanie
import motor
from motor.motor_asyncio import AsyncIOMotorClient


from app.core.config import settings
from app.models.user import User, UserRole


async def main() -> None:
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL, uuidRepresentation="standard")

    await beanie.init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[User],
    )

    email = input("Email: ").strip()
    name = input("Name: ").strip()
    password = input("Password: ")

    existing = await User.find_one(User.email == email)
    if existing is not None:
        print(f"User {email} already exists, promoting to S_ADMIN")
        existing.role = UserRole.SUPER_ADMIN
        existing.is_active = True
    else:
        super_admin = User(
            email=email,
            username=name,
            role=UserRole.SUPER_ADMIN,
            hashed_password=password,
        )
        await super_admin.insert()
    print("Done")

if __name__ == "__main__":
    main()
