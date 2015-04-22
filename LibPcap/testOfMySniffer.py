__author__ = 'michal'
from MySniffer import main, Tcp


def callback(tcp):
    print tcp.__str__()


main(callback)

