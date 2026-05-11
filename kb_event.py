from flask import render_template
import kanboard


g_columns = {}
g_users = {}
g_target_columns = []


# 初期化処理
def init(config, logger):
    global g_users, g_columns, g_target_columns

    # 設定ファイルよりtarget_columns要素を集約してリスト化
    for section in config.sections():
        columns = config.get(section, "target_columns")
        for col in columns.split(","):
            if len(col) != 0:
                g_target_columns.append(int(col))
    logger.debug(g_target_columns)

    # Kanboard APIによりユーザー一覧とカラム一覧を取得
    kb = get_kb(config, logger)
    g_users = get_users(kb, logger)
    logger.info(g_users)

    # 設定ファイル内のセクションを走査
    for section in config.sections():
        if section.isdecimal():
            # 数字のセクションはKanboardのProjectID
            # 紐付くカラムをAPIにて取得しておく。
            res = get_columns(kb, section, logger)
            g_columns.update(res)
    logger.info(g_columns)


def get_columns(kb, project_id, logger):
    result = {}
    for column in kb.get_columns(project_id=project_id):
        id = int(column["id"])
        result[id] = column["title"]

    return result


def get_users(kb, logger):
    result = {}
    for user in kb.get_all_users():
        is_active = int(user["is_active"])
        if is_active == 1:
            result[user["username"]] = user["name"]

    return result


# Kanboard APIアクセスオブジェクトを取得
def get_kb(config, logger):
    kb_conf = config["kanboard"]

    url = "{}/jsonrpc.php".format(kb_conf["url"])
    kb = kanboard.Client(url, 'jsonrpc', kb_conf["api_token"])

    return kb


# KanboardのイベントよりプロジェクトIDを取得する
def get_project_id(param):
    project_id = None

    if "event_data" in param:
        event_data = param["event_data"]
        if "task" in event_data:
            project_id = event_data["task"]["project_id"]

    return project_id


# KanbordのタスクへのURLを生成する
def get_url(config, project_id, task_id):
    return "{}/project/{}/task/{}".format(
        config.get("kanboard", "url"),
        project_id,
        task_id
    )


def get_reference_id(config, param, logger) -> str:
    result = None

    task = param["event_data"]["task"]
    if "reference" in task:
        reference = task["reference"]
        mm_url = f"{config['scheme']}://{config['host']}:{config['port']}"
        if mm_url in reference:
            result = reference.split("/")[-1]

    return result

# イベント毎のつぶやきを生成する。
def create_msg(config, param, logger):
    msg = ""

    # Kanboardのイベントを取得
    event_name = param["event_name"]
    logger.info("event_name = {}".format(event_name))

    if event_name == "task.create" or event_name == "task.move.project":
        msg = task_create_msg(config, param, logger)
    elif event_name == "task.move.column":
        msg = task_move_column_msg(config, param, logger)

    return msg


def task_create_msg(config, param, logger):
    # タスク生成イベント受信
    task = param["event_data"]["task"]
    data = {
        "creator_name": task["creator_name"],
        "title": task["title"],
        "swimlane_name": task["swimlane_name"],
        "column_title": task["column_title"],
        "category_name": task["category_name"],
        "assignee_name": task["assignee_name"],
        "url": get_url(config, task["project_id"], task["id"])
    }
    msg = render_template("task.create.j2", data=data)

    return msg


def task_move_column_msg(config, param, logger):
    msg = ""

    event_author = param["event_author"]
    if event_author in g_users:
        user_name = g_users[event_author] if g_users[event_author] is not None else "無名"
    else:
        user_info = get_user(kb, event_author)
        if user_info is not None:
            user_name = user_info["name"]
        else:
            user_name = "無名"

    changes = param["event_data"]["changes"]
    dst_column_id = int(changes["dst_column_id"])
    src_column_id = int(changes["src_column_id"])
    logger.debug("移動元カラム = {} ({})".format(src_column_id, type(src_column_id)))
    logger.debug("移動先カラム = {} ({})".format(dst_column_id, type(dst_column_id)))
    if dst_column_id in g_target_columns:
        # つぶやき対象のカラムの場合、カラムIDより名称に変換
        if dst_column_id in g_columns:
            dst_column_title = g_columns[dst_column_id]
        else:
            dst_column_title = "???"

        if src_column_id in g_columns:
            src_column_title = g_columns[src_column_id]
        else:
            src_column_title = "???"

        task = param["event_data"]["task"]
        data = {
            "user_name": user_name,
            "title": task["title"],
            "swimlane_name": task["swimlane_name"],
            "src_column_title": src_column_title,
            "dst_column_title": dst_column_title,
            "category_name": task["category_name"],
            "assignee_name": task["assignee_name"],
            "url": get_url(config, task["project_id"], task["id"])
        }
        msg = render_template("task.move.column.j2", data=data)
    else:
        logger.debug("つぶやき対象外カラム")

    return msg
