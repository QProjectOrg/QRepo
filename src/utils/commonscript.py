# -*- encoding: utf-8 -*-

import subprocess
import re
import os
import shutil
import configurer
import common
from src.utils.logger import log


def remove_dirs(dirs):
    for path_dir in dirs:
        if os.path.exists(path_dir):
            shutil.rmtree(path_dir)

def remove_file(filepath):
    os.remove(filepath)


def check_russian(path):
    print "Check russian " + path + "..."
    # print path + "/bibleqt.ini"
    file = open(path + "/bibleqt.ini", "r")
    line = file.readline()
    oldName = "empty"
    newName = oldName
    for line in file:
        line = line
        if (line.startswith("BibleShortName")):
            oldName = line.split('=')[1].lstrip().rstrip()
            oldName = unicode(oldName, "utf-8")
            newName = common.transliterate(oldName)
            if (oldName != newName):
                oldName = "BibleShortName = " + oldName
                newName = "BibleShortName = " + newName
            break
    file.close()
    common.replaceLineInFile(os.path.abspath(path + "/bibleqt.ini"), oldName, newName)


def replaceLineInFile(fileName, sourceText, replaceText):
    file = open(fileName, 'r')  # Opens the file in read-mode
    text = file.read().decode(getEncoding(fileName))  # Reads the file and assigns the value to a variable
    file.close()  # Closes the file (read session)
    file = open(fileName, 'w')  # Opens the file again, this time in write-mode
    # TODO
    # надо придумать вариант, при котором 100% заменяется именно полное слово, а не часть
    # проблема в том, что я не могу проверять на "справа конец строки" или "справа"
    # ибо это может или или, а еще могут быть, наверное, другие варианты
    # Скорее всего для моего конкретного случая (Fullname = name)
    # можно проверять на этот fullname
    newText = text.replace(sourceText, replaceText, 1)
    file.write(newText)  #replaces all instances of our keyword
    # and writes the whole output when done, wiping over the old contents of the file
    file.close()  #Closes the file (write session)
    #print 'All went well, the modifications are done'


def getEncoding(t_path):
    FileEncoding = 'utf-8'
    try:

        # get encoding from enca
        p = subprocess.Popen(configurer.CON_ENCA + " '%s'" % t_path, shell=True,
                             stdout=subprocess.PIPE)
        EncaResult = p.stdout.read()

        if EncaResult < 0:
            log("enca завершил работу некорректно, ошибка")
        else:
            # save encoding
            if (EncaResult.find("Universal transformation format 8 bits;") >= 0):
                FileEncoding = 'utf-8'
            if (EncaResult.find("Universal transformation format 16 bits;") >= 0):
                FileEncoding = 'utf-16'
            if (EncaResult.find("Universal transformation format 32 bits;") >= 0):
                FileEncoding = 'utf-32'
            if (EncaResult.find("MS-Windows code page 1251") >= 0):
                FileEncoding = "windows-1251"
            if (EncaResult.find("MS-Windows code page 1252") >= 0):
                FileEncoding = "windows-1252"
            if (EncaResult.find("MS-Windows code page 1253") >= 0):
                FileEncoding = "windows-1253"
            if (EncaResult.find("MS-Windows code page 1254") >= 0):
                FileEncoding = "windows-1254"
            if (EncaResult.find("MS-Windows code page 1255") >= 0):
                FileEncoding = "windows-1255"
            if (EncaResult.find("MS-Windows code page 1256") >= 0):
                FileEncoding = "windows-1256"
            if (EncaResult.find("MS-Windows code page 1257") >= 0):
                FileEncoding = "windows-1257"
            if (EncaResult.find("MS-Windows code page 1258") >= 0):
                FileEncoding = "windows-1258"
            if (EncaResult.find("7bit ASCII characters") >= 0):
                FileEncoding = "ascii"
            if (EncaResult.find("KOI8-R Cyrillic") >= 0):
                FileEncoding = "koi8-r"
            if (EncaResult.find("KOI8-U Cyrillic") >= 0):
                FileEncoding = "koi8-u"
            if (EncaResult.find("Unrecognized encoding") >= 0):
                FileEncoding = "utf-8"

                # if (echo_on):
                #    print ("Определение кодировки успешно выполнено.\n").decode('utf-8')

    except OSError as e:
        log("Запуск enca не удался: " + str(e))
    return FileEncoding


def getValue(Line, AddParam="_________"):
    list = []
    list.append("HTMLFilter")
    list.append("VerseSign")
    list.append("ChapterSign")

    flag = False
    for elem in list:
        if elem == AddParam:
            flag = True
            break

    # if (Line.startswith(AddParam) and (Line.find('"') != -1)):
    if Line.startswith(AddParam):
        # защита от символа "
        #TODO
        if not flag:
            return re.sub("\s+", " ", Line.replace(AddParam + " = ", "")).replace("/", "")
        else:
            return re.sub("\s+", " ", Line.replace(AddParam + " = ", ""))
    pos = Line.find("=")
    return Line[pos + 1:].strip().replace("/", "")

