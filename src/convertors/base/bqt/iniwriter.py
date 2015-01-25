# -*- encoding: utf-8 -*-
from src.utils import detectlanguage
from src.utils.common import get_conformity_bookname


class IniWriter(object):
    def __init__(self, info_dict):
        self.ini_dict = info_dict
        self.ini_text = ""

    def __write_head(self):
        """
        запись заголовка ini-файла
        :return:
        """

        rn_symbol = "\r\n"

        # copyright
        self.__add_to_ini('//// Модуль был переоформлен проектом QBible\r\n')
        self.__add_to_ini('//// Sapronov Alexander \r\n')
        self.__add_to_ini('//// e-mail: sapronov.alexander92@gmail.com \r\n')
        self.__add_to_ini('//// blog: http://blogger.sapronov.me/ \r\n\n')

        # settings
        self.__add_to_ini("BibleName = " + self.ini_dict['BibleName'] + rn_symbol)
        self.__add_to_ini("BibleShortName = " + self.ini_dict['BibleShortName'] + rn_symbol)
        self.__add_to_ini("ChapterSign = <h4>" + rn_symbol)
        self.__add_to_ini("VerseSign = <p>" + rn_symbol)

        self.__add_option_to_ini("Copyright", True)
        self.__add_to_ini(rn_symbol)

        self.__add_option_to_ini("Bible")
        self.__add_option_to_ini("OldTestament", True)
        self.__add_option_to_ini("NewTestament", True)
        self.__add_option_to_ini("Apocrypha")
        self.__add_to_ini(rn_symbol)

        self.__add_to_ini("//// Код языка: ISO 639-3" + rn_symbol)
        self.__add_option_to_ini("Language")

        self.__add_to_ini(rn_symbol)
        self.__add_option_to_ini("ChapterZero")
        self.__add_option_to_ini("StrongNumbers")
        self.__add_to_ini(rn_symbol)

        self.__add_option_to_ini("StrongsDirectory", True)
        self.__add_option_to_ini("Greek", True)
        self.__add_option_to_ini("Alphabet", True)
        self.__add_to_ini(rn_symbol)

        self.__add_option_to_ini("Categories", True)
        self.__add_to_ini(rn_symbol)

        self.__add_option_to_ini("HTMLFilter", True)
        self.__add_option_to_ini("DefaultEncoding")
        self.__add_option_to_ini("DesiredFontName", True)
        self.__add_option_to_ini("DesiredFontCharset", True)
        self.__add_option_to_ini("DesiredFontPath", True)

        self.__add_to_ini(rn_symbol)
        self.__add_to_ini("//// неофициальные параметры" + rn_symbol)
        self.__add_option_to_ini("Description", True)
        self.__add_option_to_ini("Type", True)
        self.__add_option_to_ini("Developer", True)
        self.__add_option_to_ini("DevContact", True)
        self.__add_option_to_ini("Date", True)
        self.__add_option_to_ini("Version", True)

        self.__add_to_ini(rn_symbol)
        self.__add_option_to_ini("BookQt")

        self.__add_to_ini(rn_symbol)

    def __add_option_to_ini(self, key, check=False):
        """
        Добавить в ини текст опцию с проверкой существования/без проверки существования опции
        :param key:
        :param check:
        :return:
        """
        if check:
            if self.ini_dict[key]:
                self.__add_to_ini("%s = %s" % (key, self.ini_dict.get(key)) + '\r\n')
        else:
            self.__add_to_ini("%s = %s" % (key, self.ini_dict.get(key)) + '\n')

    def __add_to_ini(self, text):
        """
        Добавить строку в текст, который сохранится в ini
        :param text:
        :return:
        """
        self.ini_text += text

    def __write_book(self, book):
        """
        запись книги в ini-файл
        :param book:
        :return:
        """
        # settings
        self.__add_to_ini("PathName = {0}\r\n".format(book.get("PathName")))
        self.__add_to_ini("FullName = {0}\r\n".format(get_conformity_bookname(book.get("FullName"))))
        self.__add_to_ini("ShortName = {0}\r\n".format(book.get("ShortName")))
        self.__add_to_ini("ChapterQty = {0}\r\n\n".format(book.get("ChapterQty")))

    def __check_language(self, book):
        if not self.ini_dict.get("Language"):
            # бывает с первого раза не верно определеяет
            lang = detectlanguage.detect(book.get("BookPathToFile"), book.get("Encoding"))
            if lang == "unkown":
                lang = detectlanguage.detect(book.get("BookPathToFile"), book.get("Encoding"))

            self.ini_dict["Language"] = lang

    def write_ini(self, file_path):
        self.__check_language(self.ini_dict.get("Books")[0].__dict__)
        self.__write_head()

        for book in self.ini_dict.get("Books"):
            self.__write_book(book.__dict__)

        f = open(file_path, "w")
        f.write(self.ini_text)
        f.close()