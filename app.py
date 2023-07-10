import sys
from datetime import datetime

from flask import Flask
from decouple import config
import redis
import psycopg2

app = Flask(__name__)

rds = None

try:
    rds = redis.Redis(host=config('REDIS_HOST_VALUE'), port=config('REDIS_PORT_VALUE'), db=0)
    rds.ping()
    print("Redis connection OK", file=sys.stderr)
except Exception as e:
    print(f"Redis connection failed: {e}", file=sys.stderr)
    exit(1)

db_conn = None

try:
    db_conn = psycopg2.connect(
        database=config('DATABASE_NAME'),
        user=config('DATABASE_USERNAME'),
        password=config('DATABASE_PASSWORD'),
        host=config('DATABASE_HOST'),
        port=config('DATABASE_PORT'),
    )
    print("Database connection OK.", file=sys.stderr)
except:
    print("Database connection failed", file=sys.stderr)
    exit(2)

with db_conn.cursor() as cur:
    cur.execute(f"""DROP TABLE IF EXISTS checked_primes;""")

    query = f"""
        CREATE TABLE if not exists checked_primes (
            id SERIAL PRIMARY KEY,
            val int NOT NULL,
            created_on TIMESTAMP NOT NULL
        );
        """
    cur.execute(query)
    db_conn.commit()

@app.route('/')
def help():
    hits = "unknown"
    try:
        rds.incr('hits')
        hits = rds.get('hits').decode('utf-8')
    except:
        pass

    list = []
    with db_conn.cursor() as cursor:
        cursor.execute(f"select * from checked_primes order by id")
        items = cursor.fetchall()

        for it in items:
            list.append((it[1], str(it[2])))
            # print(f"{it[0]}: {it[1]}")

    return f"<h1>Help Page</h1>To check if a number is prime, go to <a href='/prime/1'>/prime/&lt;N&gt;</a> where N is the number you want to check. <br> Hit count: {hits}<br><br>Checked primes:<br>{list}"

@app.route('/prime/<N>')
def check_prime(N:int):
    num = int(N)
    if num >= 1:
        for i in range(2, num):
            if (num % i) == 0:
                return "NO"
        else:
            with db_conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO checked_primes (val, created_on) VALUES (%s, %s)",
                    (num, datetime.now())
                )
                db_conn.commit()

            return "<p>YES</p><p><a href='/'>Home</a></p>"
    else:
        return "<p>NO</p><p><a href='/'>Home</a></p>"


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
