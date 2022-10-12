from vault import credentials
from freestyle.getmessages import GetMessageFreeStytle
from freestyle.icloudfile import DoubleFactorManager


def test_double_factor():
    vault_cred: credentials.CredentialsManagerVault = credentials.CredentialsManagerVault()
    assert vault_cred.icloud_user == "robcbean@gmail.com"

    get_messages: GetMessageFreeStytle = GetMessageFreeStytle(
        _user=vault_cred.glucose_user,
        _password=vault_cred.glucose_password,
        _base_url="https://api-eu.libreview.io/",
        _finger_print="3,(Macintosh;IntelMacOSX__)AppleWebKit/(KHTML,likeGecko)Version/Safari/,Mozilla/(Macintosh;IntelMacOSX__)AppleWebKit/(KHTML,likeGecko)Version/15.6.1 Safari/605.1.15,AppleGPU,Europe/Madrid,1,MacIntel,es-ES,es-ES,AppleComputer,Inc.,safari",
        _report_string_template="sdadsad",
        _past_values=1,
        _double_factor=True,
        _icloud_user=vault_cred.icloud_user,
        _icloud_password=vault_cred.icloud_password,
        _filename_token_double_factor="double_factor.txt"
    )

    assert get_messages.__send_code_url__ == "https://api-eu.libreview.io/auth/continue/2fa/sendcode"
    assert get_messages.__result_code_url__ == "https://api-eu.libreview.io/auth/continue/2fa/result"

    token_login: str = get_messages.__get_token_login__()



def test_icloud():
    vault_cred: credentials.CredentialsManagerVault = credentials.CredentialsManagerVault()
    assert vault_cred.icloud_user == "robcbean@gmail.com"

    double_factor_mgr: DoubleFactorManager = DoubleFactorManager(icloud_user=vault_cred.icloud_user,
                                                                 icloud_password=vault_cred.icloud_password,
                                                                 icloud_file="Shortcuts/libreview.txt", )

    content: str = double_factor_mgr.get_file_content()
    assert content != "" and content is not None

    code: int = double_factor_mgr.get_code_from_file_content(content)
    assert code != -1