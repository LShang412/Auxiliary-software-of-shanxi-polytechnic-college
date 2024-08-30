import requests
from ExtractInformation import extract_student_names
from ExtractVerificationCode import get_verification_code_and_rsa_modulus
from decrypt import rsa_encrypt, bytes_to_hex_upper
from utils import get_user_agent
from retry import retry


def build_login_data(username: str, password: str, rsa_modulus: str, verify_code: str) -> dict:
    return {
        "__VIEWSTATE": "tA6uBVKFegpyqnoAaHndgJpnE5COnAaCgoHV7Y3HhVb5hEH5WAjqds6F6l4ABOPYbAgvkGL8voLxZe/bkFq2R2ka+8A=",
        "__VIEWSTATEGENERATOR": "0564CA07",
        "__EVENTVALIDATION": "sn2KJ9wlNDzVvr5WZDL+uxBk4M4Wj8jgLjEjaxvHD/AYIXku5dH3FOT0SYvQ72EVlnwAQpApuHY7rcjdnwOhv"
                             "+BfNVjsDU+6LmqP0gG202suxNXXVCnDhsb5NKaurjmy6OVJqflrgAS3ZMX2ujXhFBO3ftr9sPeagR2VPoF2zDZ0"
                             "/1+9xn6yDPSWUYlnr8bgIGXbWvo2ykEr4C8/qOuNK"
                             "+tCJVrbt7r7FaSbFJdM5zgJaK7GqqZeRwRyIuMgZC1cZt0tXZ1ze6Sz3XxuTeBokkYGfxkdslj5yc1dTscLMcLQGz4Y6M0Uh0RHHaHfKO+BbJnUzxkdjpNSdASh8uV2jnP8smI=",
        "TextBox1": username,
        "TextBox2": bytes_to_hex_upper(rsa_encrypt(password, rsa_modulus)),
        "txtSecretCode": verify_code,
        "RadioButtonList1": "学生",
        "Button1": "登录",
        "txtKeyExponent": "010001",
        "txtKeyModulus": rsa_modulus,
    }


@retry(stop_exceptions=(ValueError,))
def login_jwxt_ttdk(username: str, password: str) -> requests.Session:
    session = requests.Session()
    verify_code, rsa_modulus = get_verification_code_and_rsa_modulus(session)
    data = build_login_data(username, password, rsa_modulus, verify_code)
    headers = {"User-Agent": get_user_agent()}
    response = session.post("http://jwgl.sxzy.edu.cn/", headers=headers, data=data)
    response.raise_for_status()
    if "密码错误" in response.text:
        raise ValueError("登录失败：密码错误，程序终止！")
    if "验证码不正确！！" in response.text:
        raise Exception("验证码不正确！！")
    return session


@retry(stop_exceptions=(ValueError,))
def login_jwxt(username: str, password: str) -> tuple:
    session = requests.Session()
    verify_code, rsa_modulus = get_verification_code_and_rsa_modulus(session)
    data = build_login_data(username, password, rsa_modulus, verify_code)
    headers = {"User-Agent": get_user_agent()}
    response = session.post("http://jwgl.sxzy.edu.cn/", headers=headers, data=data)
    response.raise_for_status()
    if "密码错误" in response.text:
        raise ValueError("登录失败：密码错误，程序终止！")
    if "验证码不正确！！" in response.text:
        raise Exception("验证码不正确！！")
    full_name = extract_student_names(response)
    return session, full_name


