import pytest
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests
import allure


@allure.epic("Authorization cases")
class TestUserAuth(BaseCase):
    exclude_params = [
        ("no_cookie"),
        ("no_token"),
    ]
    
    def setup_method(self):
        data = {
            'email': 'vinkotov@example.com',
            'password': '1234',
        }
        r1 = MyRequests.post("/user/login", data=data)

        self.auth_sid = self.get_cookie(response=r1, cookie_name="auth_sid")
        self.token = self.get_header(response=r1, header_name="x-csrf-token")
        self.user_id_from_auth_method = self.get_json_value(response=r1, name='user_id')
    
    
    # Позитивный тест
    @allure.description('This test successfully authorize user by email and password')
    def test_auth_user(self):

        r2 = MyRequests.get(
            "/user/auth",
            headers={'x-csrf-token': self.token},
            cookies={'auth_sid': self.auth_sid},
        )

        Assertions.assert_json_value_by_name(
            r2, 
            "user_id", 
            self.user_id_from_auth_method,
            "User id from auth method is not equal to user id from check method"
            )
    
    
    # Негативный тест
    @allure.description(
            "This test checks authorization status w/o sending auth cookie or token")
    @pytest.mark.parametrize('condition', exclude_params)
    def test_negative_auth_check(self, condition):
        
        if condition == 'no_cookie':
            r2 = MyRequests.get(
                "/user/auth",
                headers={'x-csrf-token': self.token},
            )
        else:
            r2 = MyRequests.get(
                "/user/auth",
                cookies={'auth_sid': self.auth_sid}
            )

        Assertions.assert_json_value_by_name(
            r2,
            "user_id",
            0,
            f"User is authorized with condition {condition}",
        )
        