from configparser import ConfigParser
from flask import Flask, request
import os.path
import logging.config
import kb_event
import mm_util


# 初期化処理
conf_path = os.path.join(os.path.dirname(__file__), "conf")

# Logger
logconf_file = os.path.join(conf_path, 'logging.ini')
logging.config.fileConfig(logconf_file)
logger = logging.getLogger('app')
logger.info('Start.')

# Config
config = ConfigParser()
conf_file = os.path.join(conf_path, 'config.ini')

with open(conf_file, "r") as f:
    logger.debug(f.readlines())
config.read(conf_file, 'UTF-8')
config.set('DEFAULT', 'conf_path', conf_path)

kb_event.init(config, logger)
app = Flask(__name__)


# Kanboardよりイベントを受け取るWebhook
@app.route('/hook', methods=['POST'])
def hook():
    #  Kanboardからの送信か否かtokenによりチェックする。
    token = request.args.get("token", "")
    if token != config.get('kanboard', 'token'):
        # token不一致
        logger.debug("token不一致: {}".format(token))
    else:
        param = request.get_json()
        logger.debug(param)

        # Kanboardのイベント情報よりつぶやきを生成する
        msg = kb_event.create_msg(config, param, logger)

        if msg != "":
            # イベントが紐付くプロジェクトによりチャンネルを決定する。
            project_id = kb_event.get_project_id(param)
            if project_id is not None and config.has_section(project_id):
                channel_id = config.get(project_id, "channel_id")

	            # 参照カラムにMattermostへのリンクがあったらスレッドにするため、root_idを取得
                root_id = kb_event.get_reference_id(config["mattermost"], param, logger)

                # つぶやく
                mmd = mm_util.login(config["mattermost"])[0]
                mm_util.post(mmd, msg, channel_id, logger, root_id)

    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
