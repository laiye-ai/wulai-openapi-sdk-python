"""
配置类api测试
"""
import os
import pytest

from wulaisdk.client import WulaiClient


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.smoke
@pytest.mark.parametrize('config', [
    {
        "bot_config": {
            "qa_bot_config": {"similar_response_enabled": True, "auto_response_threshold": 0.76},
            "task_bot_config": {"auto_response_threshold": 0.79}
        },
        "default_response_config": {"enabled": True},
        "customer_service_config": {"enabled": False}
    }
])
def test_update_config(config):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.update_config(config)
    assert resp.app_config.bot_config.qa_bot_config.auto_response_threshold
    assert resp.to_dict()
