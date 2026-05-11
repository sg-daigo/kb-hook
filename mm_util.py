import mattermostdriver
from requests import HTTPError
import urllib3


# オレオレ証明書の検証を無効化時にWarningを表示しない
urllib3.disable_warnings()


# mattermostへ接続
def login(config):
    option = {
        'url': config.get('host'),
        'scheme': config.get('scheme'),
        'port': int(config.get('port')),
        'token': config.get('bot_token'),
        'verify': False
    }
    driver = mattermostdriver.Driver(option)
    login_info = driver.login()

    return driver, login_info


# Mattermostでつぶやく
def post(mmd, message, channel_id, logger, root_id=""):
    try:
        options = {
            'channel_id': channel_id,
            'message': message
        }
        if root_id:
            options["root_id"] = root_id

        mmd.posts.create_post(options)
    except HTTPError as e:
        logger.error("post: " + str(e))
    except OSError as e:
        logger.error("post: " + str(e))

