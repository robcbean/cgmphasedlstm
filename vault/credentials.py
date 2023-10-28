
import os
import hvac


class CredentialsManagerVault:
    VAULT_URL: str = "VAULT_URL"
    VAULT_TOKEN: str = "VAULT_TOKEN"
    VAULT_SECRET_CGM: str = "secret/data/cgm"
    VAULT_SECRET_TELEGRAM: str = "secret/data/telegram"
    VAULT_ICLOUD: str = "secret/data/icloud"
    VAULT_USER_CGM_KEY: str = "glucose_user"
    VAULT_PASSWORD_CGM_KEY: str = "glucose_password"
    VAULT_TOKEN_TELEGRAM_KEY: str = "telegram_token"
    VAULT_CHAT_TELEGRAM_KEY: str = "telegram_chat"
    VAULT_ICLOUD_USER: str = "icloud_user"
    VAULT_ICLOUD_PASSWORD: str = "icloud_password"

    def __init__(self):
        self.client = hvac.Client(
            url=os.environ[CredentialsManagerVault.VAULT_URL],
            token=os.environ[CredentialsManagerVault.VAULT_TOKEN],
        )


    def get_value(self, secret: str, key: str) -> str:
        ret = self.client.read(secret)
        if ret != None:
            ret = ret["data"]["data"][key]
        return ret

    @property
    def icloud_user(self) -> str:
        ret: str = self.get_value(self.VAULT_ICLOUD, self.VAULT_ICLOUD_USER)
        return ret
    @property
    def icloud_password(self) -> str:
        ret: str = self.get_value(self.VAULT_ICLOUD, self.VAULT_ICLOUD_PASSWORD)
        return ret


    @property
    def glucose_user(self):
        ret = self.client.read(CredentialsManagerVault.VAULT_SECRET_CGM)
        if ret != None:
            ret = ret["data"]["data"][CredentialsManagerVault.VAULT_USER_CGM_KEY]
        return ret

    @property
    def glucose_password(self):
        ret = self.client.read(CredentialsManagerVault.VAULT_SECRET_CGM)
        if ret != None:
            ret = ret["data"]["data"][CredentialsManagerVault.VAULT_PASSWORD_CGM_KEY]
        return ret

    @property
    def telegram_token(self):
        ret = self.client.read(CredentialsManagerVault.VAULT_SECRET_TELEGRAM)
        if ret != None:
            ret = ret["data"]["data"][CredentialsManagerVault.VAULT_TOKEN_TELEGRAM_KEY]
        return ret

    @property
    def telegram_chat(self):
        ret = self.client.read(CredentialsManagerVault.VAULT_SECRET_TELEGRAM)
        if ret != None:
            ret = ret["data"]["data"][CredentialsManagerVault.VAULT_CHAT_TELEGRAM_KEY]
        return ret
