import socket
import time

def wait_for_db(host, port):
    while True:
        try:
            s = socket.create_connection((host, port), timeout=5)
            s.close()
            print("Database is ready!")
            break
        except socket.error as ex:
            print("Waiting for database...")
            time.sleep(1)

if __name__ == "__main__":
    # Wait for the service named 'db' on port 5432 (as defined in docker-compose.yml)
    wait_for_db("db", 5432)