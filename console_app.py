from client import Client
import sys


def main():
    nickname = input("Write your nickname: ")
    client = Client('127.0.0.1', 3889, nickname)
    client.set_callback(print)
    while True:
        try:
            client.write_message(input())
        except KeyboardInterrupt:
            client.stop()
            sys.exit()

if __name__ == "__main__":
    main()
