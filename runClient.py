from client import Client


def main():
    nickname = input("Write your nickname: ")
    client = Client('127.0.0.1', 3888, nickname)

if __name__ == "__main__":
    main()