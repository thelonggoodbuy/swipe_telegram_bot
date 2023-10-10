from dotenv import dotenv_values

secret_values = dotenv_values(".env")


def return_secret_value(key):
    # print(secret_values)
    return secret_values[key]