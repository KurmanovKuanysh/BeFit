# app/db/seed.py

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.config import settings
from app.db.mongo import init_db
from app.models.user import User, UserRole, ActivityLevel, Gender, Goal
from app.models.token import RefreshToken
from app.models.water import Water
from app.models.weight_log import WeightLog
from app.models.workout import (
    Exercise, ExerciseType, ExerciseCategory, MeasurementUnit, Level,
    WorkoutPlan, WorkoutPlanItem, WorkoutLog, WorkoutLogItem
)


# ========== ХЕЛПЕРЫ ==========
def hash_password_stub(password: str) -> str:
    """Заглушка для хеширования. В реальности используйте bcrypt/argon2."""
    return f"hashed_{password}"


def future_date(days: int = 7) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def past_date(days_ago: int = 1) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days_ago)


# ========== СИДЫ ==========

async def seed_users():
    """Создание тестовых пользователей"""
    users_data = [
        {
            "username": "john_doe",
            "email": "john@example.com",
            "hashed_password": hash_password_stub("password123"),
            "role": UserRole.USER,
            "age": 28,
            "height": 180.0,
            "current_weight": 82.5,
            "activity_level": ActivityLevel.MODERATELY_ACTIVE,
            "gender": Gender.MALE,
            "goal_weight": 78.0,
            "goal": Goal.WEIGHT_LOSS,
            "target_calories": 2200.0,
            "target_protein": 150.0,
            "target_fat": 60.0,
            "target_carbs": 250.0,
            "target_daily_water": 2500.0,
            "targets_auto_calculated": True,
            "is_active": True,
        },
        {
            "username": "jane_smith",
            "email": "jane@example.com",
            "hashed_password": hash_password_stub("password456"),
            "role": UserRole.USER,
            "age": 25,
            "height": 165.0,
            "current_weight": 65.0,
            "activity_level": ActivityLevel.MODERATELY_ACTIVE,
            "gender": Gender.FEMALE,
            "goal_weight": 60.0,
            "goal": Goal.MUSCLE_GAIN,
            "target_calories": 2400.0,
            "target_protein": 130.0,
            "target_fat": 70.0,
            "target_carbs": 280.0,
            "target_daily_water": 2800.0,
            "targets_auto_calculated": True,
            "is_active": True,
        },
        {
            "username": "admin_user",
            "email": "admin@example.com",
            "hashed_password": hash_password_stub("admin789"),
            "role": UserRole.ADMIN,
            "age": 35,
            "height": 175.0,
            "current_weight": 85.0,
            "activity_level": ActivityLevel.LIGHTLY_ACTIVE,
            "gender": Gender.MALE,
            "goal_weight": 82.0,
            "goal": Goal.STRENGTH_GAIN,
            "target_calories": 2500.0,
            "target_protein": 180.0,
            "target_fat": 65.0,
            "target_carbs": 300.0,
            "target_daily_water": 3000.0,
            "targets_auto_calculated": False,
            "is_active": True,
        },
    ]

    users = []
    for data in users_data:
        # Проверяем, не существует ли уже пользователь
        existing = await User.find_one({"email": data["email"]})
        if existing:
            print(f"⚠️ Пользователь {data['email']} уже существует, пропускаем")
            users.append(existing)
            continue

        user = User(**data)
        await user.insert()
        users.append(user)
        print(f"✅ Создан пользователь: {user.username} ({user.email})")

    return users


async def seed_refresh_tokens(users: list[User]):
    """Создание refresh токенов для пользователей"""
    for user in users:
        existing = await RefreshToken.find_one({"user.$id": user.id, "is_revoked": False})
        if existing:
            print(f"⚠️ Refresh токен для {user.username} уже существует, пропускаем")
            continue

        token = RefreshToken(
            user=user,
            token=f"refresh_token_{user.username}_{uuid4().hex[:16]}",
            is_revoked=False,
            expires_at=future_date(30),
        )
        await token.insert()
        print(f"🔑 Refresh token для {user.username} создан")


async def seed_water_logs(users: list[User]):
    """Логи воды для пользователей (последние 5 дней)"""
    for user in users:
        existing_count = await Water.find({"user.$id": user.id}).count()
        if existing_count > 0:
            print(f"⚠️ Записи воды для {user.username} уже существуют ({existing_count} шт.), пропускаем")
            continue

        for days_ago in range(5):
            water = Water(
                user=user,
                amount_ml=1500 + (days_ago * 200),
            )
            water.created_at = past_date(days_ago)
            water.updated_at = water.created_at
            await water.insert()
        print(f"💧 Добавлено 5 записей воды для {user.username}")


async def seed_weight_logs(users: list[User]):
    """Логи веса для пользователей"""
    weight_progress = {
        "john_doe": [82.5, 82.0, 81.2, 80.5, 79.8, 79.0],
        "jane_smith": [65.0, 65.2, 65.5, 65.8, 66.0, 66.3],
        "admin_user": [85.0, 84.7, 84.5, 84.2, 84.0, 83.8],
    }

    for user in users:
        existing_count = await WeightLog.find({"user.$id": user.id}).count()
        if existing_count > 0:
            print(f"⚠️ Записи веса для {user.username} уже существуют ({existing_count} шт.), пропускаем")
            continue

        weights = weight_progress.get(user.username, [user.current_weight] * 6)
        for i, weight in enumerate(weights):
            log = WeightLog(
                user=user,
                weight=weight,
                notes=f"Запись {i + 1}" if i % 2 == 0 else None,
            )
            log.created_at = past_date(len(weights) - i)
            log.updated_at = log.created_at
            await log.insert()
        print(f"⚖️ Добавлено {len(weights)} записей веса для {user.username}")


async def seed_exercises():
    """Создание библиотеки упражнений"""
    exercises_data = [
        {
            "name": "Жим лежа",
            "type": ExerciseType.STRENGTH,
            "description": "Классический жим штанги лежа на горизонтальной скамье",
            "category": [ExerciseCategory.CHEST, ExerciseCategory.TRICEPS],
            "measurement_unit": MeasurementUnit.KG,
            "level": Level.INTERMEDIATE,
        },
        {
            "name": "Приседания со штангой",
            "type": ExerciseType.STRENGTH,
            "description": "Базовое упражнение для ног",
            "category": [ExerciseCategory.LEG, ExerciseCategory.QUADS],
            "measurement_unit": MeasurementUnit.KG,
            "level": Level.INTERMEDIATE,
        },
        {
            "name": "Становая тяга",
            "type": ExerciseType.STRENGTH,
            "description": "Базовое упражнение для спины и ног",
            "category": [ExerciseCategory.BACK, ExerciseCategory.LEG],
            "measurement_unit": MeasurementUnit.KG,
            "level": Level.ADVANCED,
        },
        {
            "name": "Подтягивания",
            "type": ExerciseType.STRENGTH,
            "description": "Подтягивания на перекладине широким хватом",
            "category": [ExerciseCategory.BACK, ExerciseCategory.BICEPS],
            "measurement_unit": MeasurementUnit.REPS,
            "level": Level.INTERMEDIATE,
        },
        {
            "name": "Отжимания на брусьях",
            "type": ExerciseType.STRENGTH,
            "category": [ExerciseCategory.CHEST, ExerciseCategory.TRICEPS],
            "measurement_unit": MeasurementUnit.REPS,
            "level": Level.BEGINNER,
        },
        {
            "name": "Бег на беговой дорожке",
            "type": ExerciseType.CARDIO,
            "description": "Бег в умеренном темпе",
            "category": [ExerciseCategory.AEROBICS, ExerciseCategory.LEG],
            "measurement_unit": MeasurementUnit.SECONDS,
            "level": Level.BEGINNER,
        },
        {
            "name": "Велотренажер",
            "type": ExerciseType.CARDIO,
            "category": [ExerciseCategory.AEROBICS, ExerciseCategory.LEG],
            "measurement_unit": MeasurementUnit.SECONDS,
            "level": Level.BEGINNER,
        },
        {
            "name": "Планка",
            "type": ExerciseType.ENDURANCE,
            "description": "Статическое упражнение для кора",
            "category": [ExerciseCategory.CORE],
            "measurement_unit": MeasurementUnit.SECONDS,
            "level": Level.BEGINNER,
        },
        {
            "name": "Скручивания",
            "type": ExerciseType.STRENGTH,
            "category": [ExerciseCategory.CORE],
            "measurement_unit": MeasurementUnit.REPS,
            "level": Level.BEGINNER,
        },
    ]

    exercises = []
    for data in exercises_data:
        existing = await Exercise.find_one({"name": data["name"]})
        if existing:
            print(f"⚠️ Упражнение '{data['name']}' уже существует, пропускаем")
            exercises.append(existing)
            continue

        exercise = Exercise(**data)
        await exercise.insert()
        exercises.append(exercise)
        print(f"🏋️ Добавлено упражнение: {exercise.name}")

    return exercises


async def seed_workout_plans(users: list[User], exercises: list[Exercise]):
    """Создание планов тренировок"""
    exercise_map = {e.name: e for e in exercises}

    plans_data = [
        {
            "title": "Начальный план для новичков",
            "level": Level.BEGINNER,
            "created_by": users[0],
            "items": [
                {"exercise_name": "Отжимания на брусьях", "sets": 3, "reps": 8, "weight": None,
                 "duration_seconds": None},
                {"exercise_name": "Скручивания", "sets": 3, "reps": 15, "weight": None, "duration_seconds": None},
                {"exercise_name": "Бег на беговой дорожке", "sets": 1, "reps": 1, "weight": None,
                 "duration_seconds": 600},
            ]
        },
        {
            "title": "Программа для набора массы",
            "level": Level.INTERMEDIATE,
            "created_by": users[1],
            "items": [
                {"exercise_name": "Жим лежа", "sets": 4, "reps": 10, "weight": 60.0, "duration_seconds": None},
                {"exercise_name": "Приседания со штангой", "sets": 4, "reps": 12, "weight": 80.0,
                 "duration_seconds": None},
                {"exercise_name": "Подтягивания", "sets": 3, "reps": 8, "weight": None, "duration_seconds": None},
            ]
        },
        {
            "title": "Жиросжигающая тренировка",
            "level": Level.INTERMEDIATE,
            "created_by": None,
            "items": [
                {"exercise_name": "Бег на беговой дорожке", "sets": 1, "reps": 1, "weight": None,
                 "duration_seconds": 1200},
                {"exercise_name": "Приседания со штангой", "sets": 3, "reps": 15, "weight": 50.0,
                 "duration_seconds": None},
                {"exercise_name": "Планка", "sets": 3, "reps": 1, "weight": None, "duration_seconds": 45},
            ]
        },
    ]

    plans = []
    for data in plans_data:
        existing = await WorkoutPlan.find_one({"title": data["title"]})
        if existing:
            print(f"⚠️ План '{data['title']}' уже существует, пропускаем")
            plans.append(existing)
            continue

        plan = WorkoutPlan(
            title=data["title"],
            level=data["level"],
            created_by=data["created_by"],
        )
        await plan.insert()

        for item_data in data["items"]:
            exercise = exercise_map.get(item_data["exercise_name"])
            if exercise:
                item = WorkoutPlanItem(
                    workout_plan=plan,
                    exercise=exercise,
                    sets=item_data["sets"],
                    reps=item_data["reps"],
                    weight=item_data.get("weight"),
                    duration_seconds=item_data.get("duration_seconds"),
                )
                await item.insert()

        plans.append(plan)
        print(f"📋 Создан план тренировок: {plan.title}")

    return plans


async def seed_workout_logs(users: list[User], exercises: list[Exercise], plans: list[WorkoutPlan]):
    """Логи выполнения тренировок пользователями"""
    exercise_list = exercises

    # Логи для Джона
    john = users[0]
    john_plan = plans[0] if plans else None

    # Проверяем, есть ли уже логи
    existing_logs = await WorkoutLog.find({"user.$id": john.id}).count()
    if existing_logs == 0:
        # Лог тренировки по плану
        if john_plan:
            log1 = WorkoutLog(
                title="Тренировка по плану 'Начальный'",
                user=john,
                workout_plan=john_plan,
                duration_minutes=35,
                completed=True,
                completed_at=past_date(2),
            )
            await log1.insert()

            items = await WorkoutPlanItem.find({"workout_plan.$id": john_plan.id}).to_list()
            for item in items:
                log_item = WorkoutLogItem(
                    workout_log=log1,
                    exercise=item.exercise,
                    sets=item.sets,
                    reps=item.reps,
                    weight=item.weight,
                    duration_seconds=item.duration_seconds,
                )
                await log_item.insert()

        # Свободная тренировка
        log2 = WorkoutLog(
            title="Самостоятельная кардио тренировка",
            user=john,
            workout_plan=None,
            duration_minutes=45,
            completed=True,
            completed_at=past_date(1),
        )
        await log2.insert()

        free_exercises = [e for e in exercise_list if e.type == ExerciseType.CARDIO][:2]
        for ex in free_exercises:
            log_item = WorkoutLogItem(
                workout_log=log2,
                exercise=ex,
                sets=1,
                reps=1,
                weight=None,
                duration_seconds=900,
            )
            await log_item.insert()

        # Незавершенная тренировка
        log3 = WorkoutLog(
            title="Незавершенная тренировка",
            user=john,
            workout_plan=None,
            duration_minutes=None,
            completed=False,
            completed_at=None,
        )
        await log3.insert()

        print(f"📝 Созданы логи тренировок для {john.username}")
    else:
        print(f"⚠️ Логи тренировок для {john.username} уже существуют, пропускаем")

    # Логи для Джейн
    jane = users[1]
    jane_logs_count = await WorkoutLog.find({"user.$id": jane.id}).count()

    if jane_logs_count == 0 and len(plans) > 1:
        log4 = WorkoutLog(
            title="Вечерняя тренировка",
            user=jane,
            workout_plan=plans[1] if len(plans) > 1 else None,
            duration_minutes=60,
            completed=True,
            completed_at=past_date(3),
        )
        await log4.insert()

        items = await WorkoutPlanItem.find({"workout_plan.$id": plans[1].id}).to_list()
        for item in items[:2]:
            log_item = WorkoutLogItem(
                workout_log=log4,
                exercise=item.exercise,
                sets=item.sets - 1,
                reps=item.reps + 2,
                weight=item.weight,
                duration_seconds=item.duration_seconds,
            )
            await log_item.insert()

        print(f"📝 Созданы логи тренировок для {jane.username}")
    else:
        print(f"⚠️ Логи тренировок для {jane.username} уже существуют, пропускаем")


async def delete_all_data():
    """Удаление всех данных из коллекций (опционально)"""
    print("\n🧹 Удаление существующих данных...")

    collections = [
        WorkoutLogItem,
        WorkoutPlanItem,
        WorkoutLog,
        WorkoutPlan,
        Exercise,
        WeightLog,
        Water,
        RefreshToken,
        User,
    ]

    for collection in collections:
        await collection.find_all().delete()
        print(f"   - {collection.__name__}: удалено")

    print("✅ Все данные удалены\n")


# ========== ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА ==========

async def run_all_seeds(clean_first: bool = False):
    """
    Запуск всех сидов

    Args:
        clean_first: Если True, сначала удалит все существующие данные
    """
    print("\n🌱 НАЧАЛО ЗАПОЛНЕНИЯ БАЗЫ ДАННЫХ 🌱\n")
    print(f"📁 База данных: {settings.MONGODB_DB_NAME}")
    print(f"🔗 URL: {settings.MONGODB_URL}\n")

    try:
        # Инициализация подключения к БД
        await init_db()
        print("✅ Подключение к MongoDB установлено\n")

        # Очистка данных (опционально)
        if clean_first:
            await delete_all_data()

        # 1. Пользователи
        users = await seed_users()
        if not users:
            print("❌ Нет пользователей для добавления данных")
            return

        # 2. Refresh токены
        await seed_refresh_tokens(users)

        # 3. Вода
        await seed_water_logs(users)

        # 4. Вес
        await seed_weight_logs(users)

        # 5. Упражнения
        exercises = await seed_exercises()
        if not exercises:
            print("❌ Нет упражнений для добавления данных")
            return

        # 6. Планы тренировок
        plans = await seed_workout_plans(users, exercises)

        # 7. Логи тренировок
        await seed_workout_logs(users, exercises, plans)

        print("\n✅ ВСЕ ДАННЫЕ УСПЕШНО ДОБАВЛЕНЫ! ✅")

        # Статистика
        print(f"\n📊 СТАТИСТИКА:")
        print(f"   - Пользователей: {len(users)}")
        print(f"   - Упражнений: {len(exercises)}")
        print(f"   - Планов тренировок: {len(plans)}")

        # Дополнительная статистика
        water_count = await Water.find().count()
        weight_count = await WeightLog.find().count()
        log_count = await WorkoutLog.find().count()

        print(f"   - Записей воды: {water_count}")
        print(f"   - Записей веса: {weight_count}")
        print(f"   - Логов тренировок: {log_count}")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


# Точка входа
if __name__ == "__main__":
    import sys

    # Парсинг аргументов командной строки
    clean = "--clean" in sys.argv or "-c" in sys.argv

    if clean:
        print("⚠️  Включен режим полной очистки данных перед сидированием")
        response = input("Вы уверены? (y/N): ")
        if response.lower() != 'y':
            print("Операция отменена")
            sys.exit(0)

    asyncio.run(run_all_seeds(clean_first=clean))