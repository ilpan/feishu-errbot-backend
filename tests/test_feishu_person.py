from src.feishu_bot import FeishuBot
from tests import TEST_APP_SECRET_ID, TEST_APP_SECRET_KEY, TEST_OPEN_ID
import unittest

from feishu_sdk import FeishuClient
from src import FeishuPerson

class TestFeishuPerson(unittest.TestCase):
    def setUp(self) -> None:
        self.fc = FeishuClient(app_id=TEST_APP_SECRET_ID, app_secret=TEST_APP_SECRET_KEY)
    
    def test_feishu_person(self):
        fp = FeishuPerson(self.fc, TEST_OPEN_ID)
        print(f"fp: {fp}")
    
    def test_feishu_bot(self):
        fb = FeishuBot(self.fc, TEST_OPEN_ID)
        print(f"fb: {fb}")
    
if __name__ == "__main__":
    unittest.main()
