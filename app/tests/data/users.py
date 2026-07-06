users_data = [
    {
        "email": "ivan.petrov@example.com",
        "user_name": "Ivan Petrov",
        "hashed_password": "1234567891"
    },
    {
        "email": "anna.sidorova@example.com",
        "user_name": "Anna Sidorova",
        "hashed_password": "1234567891"
    },
    {
        "email": "alex.ivanov@example.com",
        "user_name": "Alex Ivanov",
        "hashed_password": "1234567891"
    },
    {
        "email": "maria.kuznetsova@example.com",
        "user_name": "Maria Kuznetsova",
        "hashed_password": "1234567891"
    },
    {
        "email": "pavel.smirnov@example.com",
        "user_name": "Pavel Smirnov",
        "hashed_password": "1234567891"
    },
]
user_data_ok = {
    "email": "ivan.petrov@example.com",
    "user_name": "Ivan Petrov",
    "hashed_password": "12345_7891"
}
user_data_user2 = {
    "email": "ivan.petrov@example.comV2",
    "user_name": "Ivan PetrovV2",
    "hashed_password": "12345_7891"
}

user_data_ok_password_v2 = {
"email": "ivan.petrov@example.com",
"user_name": "Ivan Petrov",
"password": "12345_7891"

}

user_data_wrong = {
"email": "ivan.petrov@example.com",
"user_name": 228,
"hashed_password": "1234567891"

}
user_data_exist_email = {
"email": "ivan.petrov@example.com",
"user_name": "Ivan Petrov228",
"hashed_password": "1234567891"

}
user_data_exist_name = {
"email": "ivan229.petrov@example.com",
"user_name": "Ivan Petrov",
"hashed_password": "1234567891"

}
user_data_exist_email_v2 = {
"email": "ivan.petrov@example.com",
"user_name": "Ivan Petrov228",
"password": "1234567891"

}
user_data_exist_name_v2 = {
"email": "ivan229.petrov@example.com",
"user_name": "Ivan Petrov",
"password": "1234567891"

}


user_data_update_email = {
"email": "DIPLODOCK.petrov@example.com"
}

user_data_update_all = {
"email": "DIPLODOCK.petrov@example.com",
"user_name": "Ivan Petrov DIPLODOCK"

}

user_data_update_nothing = {

}
user_data_update_existing_email = {
"email": "ivan.petrov@example.com",

}

user_data_update_existing_user_name = {
"user_name": "Ivan Petrov"

}
