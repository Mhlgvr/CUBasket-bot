import sqlite3 as sq

async def db_connect():
    global db, cur

    db = sq.connect('new.db')
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users (tg_id INTEGER PRIMARY KEY,
                    username TEXT, name TEXT, thread TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS teams (thread TEXT, name TEXT)""")

    check = cur.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
    if not check:
        cur.execute("""INSERT INTO teams (thread, name) VALUES
                    ('Запад', 'WEST'),
                    ('Восток', 'EAST'),
                    ('Север', 'NORTH'),
                    ('Юг', 'SOUTH'),
                    ('Магистратура', 'MASTERS'),
                    ('Работники', 'ELDERS')""")

    db.commit()


async def user_exists(tg_id):
    user = cur.execute("SELECT name FROM users WHERE tg_id = ?", (tg_id,)).fetchone()[0]
    if not user:
        return False
    else:
        return True

async def get_team_members(tg_id):
    members = cur.execute(f"""SELECT u2.name, u2.username FROM users u1 
    JOIN users u2 ON u1.thread = u2.thread
    WHERE u1.tg_id = {tg_id}""").fetchall()
    return [' @'.join(name) for name in members]

async def get_team_name(tg_id) -> str:
    thread = cur.execute(f"SELECT thread FROM users WHERE tg_id = {tg_id} LIMIT 1").fetchone()[0]
    team_name = cur.execute("SELECT name FROM teams WHERE thread = ?", (thread,)).fetchone()[0]
    return team_name

async def edit_team_name(tg_id: int, new_name: str) -> None:
    thread = cur.execute(f"SELECT thread FROM users WHERE tg_id = {tg_id} LIMIT 1").fetchone()[0]
    cur.execute("UPDATE teams SET name = ? WHERE thread = ?", (new_name, thread,))
    db.commit()

async def add_user(tg_id, username, name, thread):
    cur.execute("""INSERT OR REPLACE INTO users (tg_id, username, name, thread) 
    VALUES (?, ?, ?, ?)""", (tg_id, username, name, thread))
    db.commit()

async def delete_user(user_id: int) -> None:
    cur.execute("DELETE FROM users WHERE tg_id = ?", (user_id,))
    db.commit()

async def get_teams_info():
    output = ''
    team_names = cur.execute("SELECT name FROM teams").fetchall()
    for team_name in team_names:
        members = cur.execute("SELECT u.name, u.username FROM users u JOIN teams t ON t.thread = u.thread WHERE t.name = ?", (team_name[0],)).fetchall()
        output += team_name[0] + '\n' + '\n'.join([' @'.join(member) for member in members]) + '\n' + '\n'
    return output

async def get_user_ids():
    ids = cur.execute("SELECT tg_id FROM users").fetchall()
    return [user_id[0] for user_id in ids]

async def add_thread(thread, team_name):
    cur.execute("INSERT INTO teams (thread, name) VALUES", (thread, team_name,))
    db.commit()

async def get_threads():
    threads = cur.execute("SELECT thread FROM teams").fetchall()
    return [thread[0] for thread in threads]
