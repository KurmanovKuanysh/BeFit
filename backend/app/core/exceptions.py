from fastapi import status

class AppError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)

# User Errors
class UserNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"

class UserAlreadyExistsError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "User already exists"

class NotAllowedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = (
        "You are not allowed to perform this action"
    )

# Authentication Errors
class PasswordVerifyError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Password verification failed"

class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid credentials"

class InvalidTokenError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid or expired token"

# Exercise Errors
class ExerciseNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Exercise not found"

class ExerciseAlreadyExistsError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = (
        "Exercise with the same name already exists"
    )

# Workout Errors
class WorkoutPlanNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Workout not found"

class WorkoutPlanItemAlreadyExistsError(AppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Workout plan item already exists"

class WorkoutPlanItemNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Workout plan item not found"

class WorkoutLogItemNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Workout log item not found"

class WorkoutDataEmptyError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Workout data is empty"

class WorkoutLogNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Workout log not found"

# Water Log Errors
class WaterLogNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Water log not found"

class WeightLogNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Weight log not found"