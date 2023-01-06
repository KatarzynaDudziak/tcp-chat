from client import Client


def main():
    nickname = input("Write your nickname: ")
    client = Client('127.0.0.1', 3889, nickname)
    client.set_callback(print)
    while True:
        client.write_message(input())
    client.stop()


if __name__ == "__main__":
    main()
