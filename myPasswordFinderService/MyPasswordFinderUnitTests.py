__author__ = 'michal'

import unittest
from myPasswordFinderService.MyPasswordFinder import MyPasswordFinder


class StorageUnitTest(unittest.TestCase):
    def find_pass_test(self):
        with open('Post.txt', 'rU') as f:
            read_data = f.read()
            finder = MyPasswordFinder().find_pass_in_http_message(read_data)
            print finder
            assert type(finder) is dict or finder is None

    def find_pass_test2(self):
        http = {
        u'header': u'POST /logowanie HTTP/1.1\r\nHost: electropark.pl\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: pl,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nReferer: http://electropark.pl/logowanie\r\nCookie: 8812c36aa5ae336c2a77bf63211d899a=AmbSZU%2BCsu1YM8GNBNTGS%2Bu4lCoV%2BiO8KBO0EG3UniGcdL9nhRnks9%2B0s80Jf826Uj%2F1yPm7gJ6nH5DZXzlVU5JUMBX04yEoshlYnsRo9kZvMlmqS8aPVwFMjW9GP%2Fzd73ZEeEVcNlQV%2FlMHzo6L9txWCixgYSvkVVkgVY9RGRE%3D000115; __utma=99331018.1656634180.1430216094.1430223055.1430226955.3; __utmc=99331018; __utmz=99331018.1430216094.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); cookies_accepted=T; __utmb=99331018.1.10.1430226955\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 66',
        u'request_line': u'POST /logowanie HTTP/1.1',
        u'fields': {u'Content-Length': u'66',
                    u'Accept-Language': u'pl,en-US;q=0.7,en;q=0.3',
                    u'Accept-Encoding': u'gzip, deflate',
                    u'Host': u'electropark.pl',
                    u'Accept': u'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    u'User-Agent': u'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0',
                    u'Connection': u'keep-alive',
                    u'Referer': u'http://electropark.pl/logowanie',
                    u'Cookie': u'8812c36aa5ae336c2a77bf63211d899a=AmbSZU%2BCsu1YM8GNBNTGS%2Bu4lCoV%2BiO8KBO0EG3UniGcdL9nhRnks9%2B0s80Jf826Uj%2F1yPm7gJ6nH5DZXzlVU5JUMBX04yEoshlYnsRo9kZvMlmqS8aPVwFMjW9GP%2Fzd73ZEeEVcNlQV%2FlMHzo6L9txWCixgYSvkVVkgVY9RGRE%3D000115; __utma=99331018.1656634180.1430216094.1430223055.1430226955.3; __utmc=99331018; __utmz=99331018.1430216094.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); cookies_accepted=T; __utmb=99331018.1.10.1430226955',
                    u'Content-Type': u'application/x-www-form-urlencoded'},
        u'data': u'\r\nemail=geabaeph%40dodsi.com&passwd=asdfasdfasdf&SubmitLogin=Zaloguj\r\n'}

        finder = MyPasswordFinder().find_pass(http)
        print finder
        assert type(finder) is dict or finder is None