from vault import credentials
from freestyle.getmessages import GetMessageFreeStytle

def test_double_factor():
    vault_cred: credentials.CredentialsManagerVault  = credentials.CredentialsManagerVault()
    assert vault_cred.icloud_user == "robcbean@gmail.com"

    get_messages: GetMessageFreeStytle = GetMessageFreeStytle(
                _user=vault_cred.glucose_user,
                _password=vault_cred.glucose_password,
                _base_url="https://api-eu.libreview.io/",
                _finger_print = "3,(Macintosh;IntelMacOSX__)AppleWebKit/(KHTML,likeGecko)Version/Safari/,Mozilla/(Macintosh;IntelMacOSX__)AppleWebKit/(KHTML,likeGecko)Version/15.6.1 Safari/605.1.15,AppleGPU,Europe/Madrid,1,MacIntel,es-ES,es-ES,AppleComputer,Inc.,safari",
                _report_string_template="",
                _past_values=1,
                _double_factor=True
    )

    assert get_messages.__send_code_url__ == "https://api-eu.libreview.io/auth/continue/2fa/sendcode"
    assert get_messages.__result_code_url__ == "https://api-eu.libreview.io/auth/continue/2fa/result"

    token_single_factor = get_messages.__token_login_single_factor__()
    get_messages.__request_send_code_to_mobile__(token_single_factor)










