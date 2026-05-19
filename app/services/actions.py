from enum import Enum

class Actions(str, Enum):
    get_salt = "get salt"
    create_user = "User created"
    create_session = "Register"
    log_in_account = "Log in in the account"
    logout = "Log out"
    update_user_settings = "UPDATE user settings"
    new_vault = "New vault created"
    modify_vault = "MODIFY vault"
    delete_vault = "DELETE vault"
    new_login = "New login created"
    modify_login = "MODIFY login"
    delete_login = "Delete login"
    upload_file = "Upload file"
    delete_file = "Delete file"

class Results(str, Enum):
    fail = "Fail"
    success = "Success"