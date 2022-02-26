import os
import hvac

class CredentialsManagerVault:
    VAULT_URL = "VAULT_URL"
    VAULT_TOKEN = "VAULT_TOKEN"
    VAULT_SECRET_CGM = "secret/data/cgm"
    VAULT_SECRET_TELEGRAM = "secret/data/telegram"
    VAULT_USER_CGM_KEY = "glucose_user"
    VAULT_PASSWORD_CGM_KEY = "glucose_password"
    VAULT_TOKEN_TELEGRAM_KEY = "telegram_token"
    VAULT_CHAT_TELEGRAM_KEY = "telegram_chat"
    def __init__(self):
        self.client = hvac.Client(url=os.environ[CredentialsManagerVault.VAULT_URL],token=os.environ[CredentialsManagerVault.VAULT_TOKEN])

    @property
    def glucose_user(self):
        ret = self.client.read(CredentialsManagerVault.VAULT_SECRET_CGM)
        if ret != None:
            ret = ret['data']['data'][CredentialsManagerVault.VAULT_USER_CGM_KEY]
        return ret

    @property
    def glucose_password(self):
        ret = self.client.read(CredentialsManagerVault.VAULT_SECRET_CGM)
        if ret != None:
            ret = ret['data']['data'][CredentialsManagerVault.VAULT_PASSWORD_CGM_KEY]
        return ret

    @property
    def telegram_token(self):
        ret = self.client.read(CredentialsManagerVault.VAULT_SECRET_TELEGRAM)
        if ret != None:
            ret = ret['data']['data'][CredentialsManagerVault.VAULT_TOKEN_TELEGRAM_KEY]
        return ret

    @property
    def telegram_chat(self):
        ret = self.client.read(CredentialsManagerVault.VAULT_SECRET_TELEGRAM)
        if ret != None:
            ret = ret['data']['data'][CredentialsManagerVault.VAULT_CHAT_TELEGRAM_KEY]
        return ret

