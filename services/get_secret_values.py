from dotenv import dotenv_values

secret_values = dotenv_values(".env")


def return_secret_value(key):
    return secret_values[key]