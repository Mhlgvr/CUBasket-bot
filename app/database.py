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
    data = {}
    output = ''
    threads = ['Север', 'Юг', 'Запад', 'Восток', 'Магистратура', 'Работники']
    for thread in threads:
        team_name = cur.execute("SELECT name FROM teams WHERE thread = ?", (thread,)).fetchone()[0]
        members = cur.execute("SELECT name, username FROM users WHERE thread = ?", (thread,)).fetchall()
        data.update({team_name: [' @'.join(name) for name in members]})
        output += team_name + '\n' + '\n'.join(data[team_name]) + '\n' + '\n'
    return output
