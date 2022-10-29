import os
from vault import credentials
from main import CgmPhasedLSTM

def test_until() -> None:

    os.chdir(os.path.dirname(__file__))

    configFile = "config_linux.json"
    vault_cred_mgr = credentials.CredentialsManagerVault()

    freeStyleML = CgmPhasedLSTM(
        _config_file=configFile,
        _cont_glucose_user=vault_cred_mgr.glucose_user,
        _cont_glucose_pass=vault_cred_mgr.glucose_password,
        _telegram_chat=vault_cred_mgr.telegram_chat,
        _telegram_token=vault_cred_mgr.telegram_token,
        _icloud_user=vault_cred_mgr.icloud_user,
        _icloud_password=vault_cred_mgr.icloud_password
    )

    until_schedule_func: str = freeStyleML.get_until_schedule()
    assert until_schedule_func == "2022-10-30 01:59"
