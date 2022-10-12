from vault import credentials
from freestyle.getmessages import GetMessageFreeStytle


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

token_login: str = get_messages.__get_token_login__()