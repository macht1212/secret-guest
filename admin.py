import asyncio
import getpass

import click

from src.models.users import UserRole
from src.schemas.user import UserAdd
from src.utils.db_manager import DBManager
from src.services.auth import AuthService
from src.database import async_sessionmaker_local

auth = AuthService()


async def create_admin_user(email: str, password: str, first_name: str = "Admin", last_name: str = "User"):
    async with DBManager(session_factory=async_sessionmaker_local) as session:
        existing_user = await session.users.get_one_or_none(email=email)
        if existing_user:
            click.echo(click.style(f"Пользователь с email {email} уже существует.", fg="yellow"))
            return

        hashed_password = auth.create_hashed_password(password)
        new_admin = UserAdd(
            email=email,
            first_name=first_name,
            middle_name="None",
            last_name=last_name,
            hashed_password=hashed_password,
            city="None",
            country="None",
            role=UserRole.ADMIN.value,
            phone="None",
        )

        await session.users.add(new_admin)
        await session.commit()

        click.echo(click.style(f"✅ Администратор {email} успешно создан!", fg="green"))


@click.command()
@click.option("--email", prompt="Email администратора", help="Email нового администратора")
@click.option("--first-name", prompt="Имя", default="Admin", help="Имя администратора")
@click.option("--last-name", prompt="Фамилия", default="User", help="Фамилия администратора")
def create_admin(email: str, first_name: str, last_name: str):
    """Создать администратора в системе."""
    password = getpass.getpass("Пароль администратора (не отображается): ")
    if not password:
        click.echo(click.style("❌ Пароль не может быть пустым.", fg="red"))
        return

    asyncio.run(create_admin_user(email, password, first_name, last_name))


if __name__ == "__main__":
    create_admin()
