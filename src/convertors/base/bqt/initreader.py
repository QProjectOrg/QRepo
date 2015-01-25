# -*- encoding: utf-8 -*-
import datetime
import os
import string

from src.convertors.base.bqt.currentbooksettings import CurrentBookSettings
from src.utils import commonscript
from src.utils.logger import log
from src.convertors.base.bqt.bqtdata import *
from src.utils.common import getFileNameInProperCase


class IniReader():
    class CCurrentBookSettings(CurrentBookSettings):
        pass

    def __init__(self, ini_path):
        self.input_filename = ini_path
        self.ini_file = file(self.input_filename, 'r')

        self.__set_default_values()


    def __set_default_values(self):
        self.Books = []
        self.CurrentBookSettings = self.CCurrentBookSettings()

        self.IniDesiredFontName = ""

        self.init_values()

    def init_data(self, dict_data):
        self.ini_type = dict_data.get("IniType")
        self.module_type = dict_data.get("ModuleType")
        # self.INIEncoding = dict_data.get("INIEncoding")
        self.ini_encoding = commonscript.getEncoding(self.input_filename)
        self.module_directory = dict_data.get("ModuleDirectory")

    def init_values(self):
        self.introduction_exist = False
        self.strongs_exist = False

        self.ini_chapter_zero = 'N'
        self.ini_apocrypha = 'N'
        self.ini_strong_numbers = 'N'
        self.ini_old_testament = ""
        self.ini_new_testament = ""
        self.ini_copyright = ""
        self.ini_categories = ""
        self.ini_greek = ""
        self.ini_bible = "Y"
        self.ini_desired_fontcharset = ""
        self.ini_htmlfilter = ""
        self.ini_alphabet = ""
        self.ini_strongs_dDirectory = ""
        self.ini_default_encoding = "utf-8"
        self.ini_language = ""
        self.ini_desired_fontpath = ""
        self.ini_bookqt = 0
        self.ini_bookchaptersign = ""
        self.ini_bookversesign = ""

        self.ini_developer = ""
        self.ini_devcontact = ""
        self.ini_date = datetime.date.today()
        self.ini_version = "1.0"

        self.ini_description = ""

        self.ini_dict = {}

    # разбор bibleqt.ini
    def parse_ini(self):

        general_settings_parsed = False
        self.init_values()

        for line in self.ini_file:
            # перекодируем строки в UTF-8
            line = line.decode(self.ini_encoding).encode('utf_8').strip()
            # Line = Line.decode('utf_8').strip()
            # обработка основных параметров модуля
            if not general_settings_parsed:
                general_settings_parsed = self.__parse_general_settings(line)
            else:
                # обработка параметров конкретной книги модуля
                self.__parse_book_settings(line)

    def __generate_ini_dict(self):
        ini_dict = {}
        ini_dict['DesiredFontName'] = self.IniDesiredFontName
        ini_dict['BibleName'] = self.HeadBibleName
        ini_dict['BibleShortName'] = self.HeadBibleShortName
        ini_dict['ChapterZero'] = self.ini_chapter_zero
        ini_dict['Apocrypha'] = self.ini_apocrypha
        ini_dict['StrongNumbers'] = self.ini_strong_numbers
        ini_dict['OldTestament'] = self.ini_old_testament
        ini_dict['NewTestament'] = self.ini_new_testament
        ini_dict['Copyright'] = self.ini_copyright
        ini_dict['Categories'] = self.ini_categories
        ini_dict['Greek'] = self.ini_greek
        ini_dict['Bible'] = self.ini_bible
        ini_dict['DesiredFontCharset'] = self.ini_desired_fontcharset
        ini_dict['HTMLFilter'] = self.ini_htmlfilter
        ini_dict['Alphabet'] = self.ini_alphabet
        ini_dict['StrongsDirectory'] = self.ini_strongs_dDirectory
        ini_dict['DefaultEncoding'] = self.ini_default_encoding
        ini_dict['Language'] = self.ini_language
        ini_dict['DesiredFontPath'] = self.ini_desired_fontpath
        ini_dict['BookQt'] = self.ini_bookqt
        ini_dict['ChapterSign'] = self.ini_bookchaptersign
        ini_dict['VerseSign'] = self.ini_bookversesign

        ini_dict['Type'] = self.ini_type
        ini_dict['Developer'] = self.ini_developer
        ini_dict['DevContact'] = self.ini_devcontact
        ini_dict['Date'] = self.ini_date
        ini_dict['Version'] = self.ini_version
        ini_dict['Description'] = self.ini_description

        ini_dict['Books'] = self.Books

        return ini_dict

        # self.IniDict[''] = self.Ini

    def __parse_general_settings(self, line):

        # название модуля и короткое название
        if line.startswith('BibleName'):
            self.HeadBibleName = commonscript.getValue(line)
            return False

        # название модуля и короткое название
        if line.startswith('Bible '):
            self.ini_bible = commonscript.getValue(line)
            return False

        if line.startswith('BibleShortName'):
            self.HeadBibleShortName = commonscript.getValue(line)
            self.__check_module_name(self.HeadBibleShortName)
            if self.module_type == 'Apocrypha':
                self.HeadBibleShortName += '-Apocrypha'
            return False
        # начинается ли в модуле исчисление глав с нуля
        if line.startswith('ChapterZero'):
            self.ini_chapter_zero = commonscript.getValue(line)
            if self.ini_chapter_zero == 'Y':
                self.introduction_exist = True
                self.OsisWriter.RemakeVersificationProblems()
            return False
        # считываем признак начала главы в HTML файле
        if line.startswith('ChapterSign'):
            self.ini_bookchaptersign = commonscript.getValue(line, "ChapterSign")
            return False
        # считываем копирайт
        if line.startswith('Copyright'):
            self.ini_copyright = commonscript.getValue(line)
            return False

        if line.startswith('Alphabet'):
            self.ini_alphabet = commonscript.getValue(line)
            return False

        if line.startswith('HTMLFilter'):
            self.ini_htmlfilter = commonscript.getValue(line, "HTMLFilter")
            return False

        if line.startswith('DesiredFontCharset'):
            self.ini_desired_fontcharset = commonscript.getValue(line)
            return False

        # считываем грееческий
        if line.startswith('Greek'):
            self.ini_greek = commonscript.getValue(line)
            return False

        # считываем категории
        if line.startswith('Categories'):
            self.ini_categories = commonscript.getValue(line)
            return False

        if line.startswith('StrongsDirectory'):
            self.ini_strongs_dDirectory = commonscript.getValue(line)
            return False

        # считываем признак начала стиха
        if line.startswith('VerseSign'):
            self.ini_bookversesign = commonscript.getValue(line, "VerseSign")
            return False

        if line.startswith('DesiredFontName'):
            self.IniDesiredFontName = commonscript.getValue(line)
            return False

        if line.startswith('OldTestament'):
            self.ini_old_testament = commonscript.getValue(line)
            return False

        if line.startswith('NewTestament'):
            self.ini_new_testament = commonscript.getValue(line)
            return False

        # выводим сообщение о том, что программа не обрабатывает апокрифы
        if line.startswith('Apocrypha'):
            self.ini_apocrypha = commonscript.getValue(line)
            if self.ini_apocrypha == 'Y' and \
                    not self.module_type == 'Apocrypha':
                log("""
                    Скрипт не обрабатывает апокрифы, в связи с тем, что на
                    данный момент библиотека Sword не поддерживает апокрифы
                    в библейских модулях. Если вам все же нужны апокрифы, то
                    запустите скрипт с параметром "--moduletype Apocrypha",
                    чтобы получить модуль, содержащий только апокрифы в формате
                    обычной книги.
                    """)
            return False
        # определяем наличие в модуле номеров Стронга
        if line.startswith('StrongNumbers'):
            self.ini_strong_numbers = commonscript.getValue(line)
            if self.ini_strong_numbers == 'Y' and self.module_type not in JustBooks:
                self.strongs_exist = True
            return False
        # считываем количество книг
        if line.startswith('BookQty'):
            self.ini_bookqt = commonscript.getValue(line)
            self.IniBookCount = 0
            return True

        # мои опции
        if line.startswith('Description'):
            self.ini_description = commonscript.getValue(line)
            return False

        if line.startswith('Developer'):
            self.IniDevelop = commonscript.getValue(line)
            return False

        if line.startswith('Date'):
            self.ini_date = commonscript.getValue(line)
            return False

        if line.startswith('Version'):
            self.ini_version = commonscript.getValue(line)
            return False

        if line.startswith('Type'):
            self.ini_type = commonscript.getValue(line)
            return False

    def __parse_book_settings(self, line):
        # считываем имя файла, относительно текущей директории
        if line.startswith('PathName'):
            self.CurrentBookSettings.PathName = "book_" + str(self.IniBookCount + 1) + \
                                                '.html'
            self.CurrentBookSettings.BookPathToFile = self.module_directory + commonscript.getValue(line)
            return
        # ищем соответвие длинного названия книги и короткого
        if line.startswith('ShortName') and self.module_type != 'Book':
            self.CurrentBookSettings.ShortName = commonscript.getValue(line)

            if not self.CurrentBookSettings.ShortName:
                self.CurrentBookSettings.ShortName = "Empty ShortName"
                if not self.CurrentBookSettings.FullName:
                    self.CurrentBookSettings.FullName = "Empty FullName"
                return
            # TODO переписать этот блок по нормальному
            for Pair in TableBooks:
                if Pair[0] in line:
                    # self.CurrentBookSettings.FullName = Pair[1]
                    # self.CurrentBookSettings.Testament = Pair[2]
                    if Pair[2] == 3 and \
                            not self.module_type == 'Apocrypha':
                        log('ПРЕДУПРЕЖДЕНИЕ: ', self.CurrentBookSettings.FullName, ' - апокрифическая книга.')
                        # self.CurrentBookSettings.FullName = ''
                    elif Pair[2] != 3 and self.module_type == 'Apocrypha':
                        log('ПРЕДУПРЕЖДЕНИЕ: ' + \
                            self.CurrentBookSettings.FullName + \
                            ' - каноническая книга.')
                        # self.CurrentBookSettings.FullName = ''
                    break
                if Pair == TableBooks[len(TableBooks) - 1]:
                    # self.CurrentBookSettings.FullName = Pair[1]
                    # self.CurrentBookSettings.FullName = commonscript.getValue(Line)
                    log('Ошибка, не найдено название книги "' + self.CurrentBookSettings.FullName + '"')

        # сохраняем название книги
        if line.startswith('FullName') and (self.module_type != 'Dictionary'):
            self.CurrentBookSettings.FullName = commonscript.getValue(line)
            return False

        # переходим к чтению файла книги
        if line.startswith('ChapterQty') and self.CurrentBookSettings.FullName != '':

            if os.path.exists(getFileNameInProperCase(self.CurrentBookSettings.BookPathToFile)):

                self.CurrentBookSettings.BookPathToFile = getFileNameInProperCase(
                    self.CurrentBookSettings.BookPathToFile)

                BookFile = file(getFileNameInProperCase(self.CurrentBookSettings.BookPathToFile), 'r')
                self.CurrentBookSettings.ChapterQty = commonscript.getValue(line)
                # печатаем книгу в ini файл

                log('Обрабатываю файл ' + self.CurrentBookSettings.BookPathToFile)
                self.CurrentBookSettings.Encoding = commonscript.getEncoding(self.CurrentBookSettings.BookPathToFile)
                self.CurrentBookSettings.ChapterSign = self.ini_bookchaptersign
                self.Books.append(self.CurrentBookSettings)
                self.CurrentBookSettings = self.CCurrentBookSettings()
                self.IniBookCount += 1
                BookFile.close()
            else:
                print "Not found file " + getFileNameInProperCase(self.CurrentBookSettings.BookPathToFile)

    def __check_module_name(self, name):
        for i in xrange(0, len(name)):
            if not name[i] in string.printable:
                log('ПРЕДУПРЕЖДЕНИЕ: имя модуля содержит нелатинские\n'
                    'символы. Итоговый модуль Sword не будет работать\n'
                    'в некоторых фронтендах. Например BibleTime.\n')
                return

    def get_ini_info(self):
        return self.__generate_ini_dict()