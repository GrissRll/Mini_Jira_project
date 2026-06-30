users_data = [
    {
        "email": "ivan.petrov@example.com",
        "user_name": "Ivan Petrov",
    },
    {
        "email": "anna.sidorova@example.com",
        "user_name": "Anna Sidorova",
    },
    {
        "email": "alex.ivanov@example.com",
        "user_name": "Alex Ivanov",
    },
    {
        "email": "maria.kuznetsova@example.com",
        "user_name": "Maria Kuznetsova",
    },
    {
        "email": "pavel.smirnov@example.com",
        "user_name": "Pavel Smirnov",
    },
]
user_data_ok = {
    "email": "ivan.petrov@example.com",
    "user_name": "Ivan Petrov",
}

user_data_wrong = {
    "email": "ivan.petrov@example.com",
    "user_name": 228,
}
user_data_exist_email = {
    "email": "ivan.petrov@example.com",
    "user_name": "Ivan Petrov228",
}
user_data_exist_name = {
    "email": "ivan229.petrov@example.com",
    "user_name": "Ivan Petrov",
}