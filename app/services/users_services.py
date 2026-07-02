from app.schemas.users import CreateUserSchema, UpdateUserSchema
from app.repositories.users import UserRepository
from app.models.users import User as UserModel
from app.exeptions.users_exeptions import *
from sqlalchemy.exc import IntegrityError


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    async def create_user(self, user: CreateUserSchema) -> UserModel:
        """
            Create new user after validation.
            Raise exception if user name or email already exists.
            Return created user.
        """
        filters = self.user_repo._build_or_filter(user.user_name, user.email)
        existing_user = await self.user_repo.get_user_on_filters(filters)
        if existing_user:
            if existing_user.user_name == user.user_name:
                raise UserNameAlreadyExistsError()
            if existing_user.email == user.email:
                raise UserEmailAlreadyExistsError()
        new_user = await self.user_repo.create(user)
        # На гонку не написан тест...пока посидит
        try:
            await self.user_repo.db.commit()
            return new_user
        except IntegrityError as exc:
            raise UserAlreadyExistsError() from exc

    async def get_all_users(self,
                            page_num: int = 1,
                            page_size: int = 10, ) -> list[UserModel]:
        """
            Get paginated users list.
            Return list of users.
        """

        filters = self.user_repo._buid_and_filter()
        users = await self.user_repo.get_users_on_filters(filters, page_num, page_size)
        return users

    async def get_user_by_id(self, user_id: int) -> UserModel:
        """
            Get user by identifier.
            Raise exception if user does not exist.
            Return user.
        """

        filters = self.user_repo._buid_and_filter(user_id=user_id)
        existing_user = await self.user_repo.get_user_on_filters(filters)
        if not existing_user:
            raise UserNotFoundError()
        return existing_user

    async def update_user(self, updated_data: UpdateUserSchema, user: UserModel,
                          user_id: int) -> UserModel:
        """
            Update user data after validation.
            Raise exception if user is forbidden, user does not exist,
            invalid data is provided or unique fields already exist.
            Return updated user.
        """
        if user.id != user_id:
            raise UserForbiddenError()

        updated_data = updated_data.model_dump(exclude_unset=True)
        for key in updated_data:
            if updated_data[key] is None and (key == "email" or key == "user_name"):
                raise UserInvalidData(key, "cannot be null")
            if key == "email" or key == "user_name":
                filters = self.user_repo._buid_and_filter(**{key: updated_data[key]})
                existing_key = await self.user_repo.get_user_on_filters(filters)
                if existing_key and key == "email":
                    raise UserEmailAlreadyExistsError()
                if existing_key and key == "user_name":
                    raise UserNameAlreadyExistsError()

        try:
            user = await self.user_repo.update(user, updated_data)
            await self.user_repo.db.commit()
            return user
        except IntegrityError as exc:
            await self.user_repo.db.rollback()
            error = str(exc.orig)
            if "un_users_email" in error:
                raise UserEmailAlreadyExistsError
            if "un_users_user_name" in error:
                raise UserNameAlreadyExistsError
            raise
