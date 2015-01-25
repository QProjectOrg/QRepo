# -*- encoding: utf-8 -*-

from src.utils.logger import log
import sys
import os
import shutil
import zipfile
import fnmatch
import subprocess
import re
import shlex
import commonscript
import configurer

import MySQLdb
import string


def get_conformity_bookname(bookName):
    new_bookname = bookName

    # fix
    table_bookNames_russian = [
        ['Gen', 'Бытие'],
        ['Exod', 'Исход'], ['Lev', ''],
        ['Num', 'Числа'], ['Deut', ''],
        ['Josh', 'Иисус Навин'], ['Judg', ''],
        ['Ruth', 'Руфь'], ['1Sam', '1-ая Царств'],
        ['2Sam', '2-я Царств'], ['1Kgs', '3-я Царств'],
        ['2Kgs', '4-я Царств'], ['1Chr', '2-я Паралипоменон'],
        ['2Chr', '2-я Паралипоменон'], ['Ezra', 'Ездра'],
        ['Neh', 'Неемия'], ['Esth', 'Есфирь'],
        ['Job', 'Иов'], ['Ps', 'Псалтирь'],
        ['Prov', 'Притчи'], ['Eccl', 'Екклесиаст'],
        ['Song', 'Песни Песней'], ['Isa', 'Исаия'],
        ['Jer', 'Иеремия'], ['Lam', 'Плач Иеремии'],
        ['Ezek', 'Иезекииль'], ['Dan', 'Даниил'],
        ['Hos', 'Осия'], ['Joel', 'Иоиль'],
        ['Amos', 'Амос'], ['Obad', 'Авдий'],
        ['Jonah', 'Иона'], ['Mic', 'Михей'],
        ['Nah', 'Наум'], ['Hab', 'Аввакум'],
        ['Zeph', 'Софония'], ['Hag', 'Аггей'],
        ['Zech', 'Захария'],
        ['Mal', 'Малахия'],  #до сюда
        ['Matt', 'От Матфея'],  # от сюда греческие
        ['Mark', 'От Марка'], ['Luke', 'от Луки'],
        ['John', 'От Иоанна'], ['Acts', 'Деяния'],
        ['Jas', 'Иакова'], ['1Pet', '1-е Петра'],
        ['2Pet', '2-е Петра'], ['1John', '1-е Иоанна'],
        ['2John', '2-е Иоанна'], ['3John', '3-е Иоанна'],
        ['Jude', 'Иуда'], ['Rom', 'К Римлянам'],
        ['1Cor', '1-е Коринфянам'], ['2Cor', '2-е Коринфянам'],
        ['Gal', 'К Галатам'], ['Eph', 'К Ефесянам'],
        ['Phil', 'К Филиппийцам'], ['Col', 'К Колоссянам'],
        ['1Thess', '1-е Фессалоникийцам'], ['2Thess', '1-е Фессалоникийцам'],
        ['1Tim', '1-е Тимофею'], ['2Tim', '2-е Тимофею'],
        ['Titus', 'К Титу'], ['Phlm', 'К Филимону'],
        ['Heb', 'К Евреям'],
        ['Rev', 'Откровение'],  #до сюда
        ['1Mac', '1 кн. Маккавейская*'], ['2Mac', '2 кн. Маккавейская*'],
        ['3Mac', '3 кн. Маккавейская*'],
        ['4Mac', '4 кн. Маккавейская*'], ['Bar', 'Варух*'],
        ['2Esd', '2 кн. Ездры*'], ['3Esd', '3 кн. Ездры*'],
        ['Judith', 'Иудифь*'], ['EpJer', 'Послание Иеремии*'],
        ['WSo', 'Премудрость Соломона*'], ['Sir', 'Сирах*'],
        ['Tob', 'Товит*'], ['Prim', 'Примечание'],
    ]

    for Pair in table_bookNames_russian:
        if Pair[0] == bookName:
            new_bookname = Pair[1]
    return new_bookname

def move_file(input_file, output_folder):
    file_name = os.path.basename(input_file)
    moved_file = output_folder + "/" + file_name
    os.rename(input_file, moved_file)

def move_file2file(input_file, output_file):
    (path, filename) = os.path.split(output_file)
    if not os.path.isdir(os.path.abspath(path)):
        os.makedirs(os.path.abspath(path))
    os.rename(os.path.abspath(input_file), os.path.abspath(output_file))


def replaceFileToFile(inputFile, outputFile):
    (path, file) = os.path.split(outputFile)
    if not os.path.isdir(os.path.abspath(path)):
        os.makedirs(os.path.abspath(path))
    if (os.path.exists(outputFile)):
        os.remove(os.path.abspath(outputFile))
    os.rename(os.path.abspath(inputFile), os.path.abspath(outputFile))



def copyFileToFile(inputFile, outputFile):
    (path, file) = os.path.split(outputFile)
    #print path
    if not os.path.isdir(os.path.abspath(path)):
        os.makedirs(os.path.abspath(path))
    shutil.copyfile(os.path.abspath(inputFile), os.path.abspath(outputFile))

def addFileWithTextInZip(zipPath, text, textFile):
    z = zipfile.ZipFile(zipPath, 'a')
    # Добавление буфера/строки в архив как файл
    z.writestr(textFile, text)
    z.close()


def getValue(Line, AddParam="_________"):
    if (Line.startswith(AddParam) and (Line.find('"') != -1)):
        # защита от символа "
        #TODO
        return re.sub("\s+", " ", Line.replace(AddParam + " = ", ""))
    pos = Line.find("=")
    return Line[pos + 1 :].strip()


def getFilesWithExt(dir, ext):
    files = os.listdir(dir);
    filterFiles = filter(lambda x: x.lower().endswith(ext), files);
    return filterFiles

def getZipFilesInFolder(dir):
    return getFilesWithExt(dir, ".zip")

def findFileWithFilter(path, filter):
    #print os.path.abspath(path)
    #print "Find file..."
    for root, dirs, files in os.walk(os.path.abspath(path)):
        for name in files:
            #print name
            if fnmatch.fnmatch(name.lower(), filter):
                return os.path.abspath(path + "/" + name)



def getTypeFromInfo(dirName):
    filePath = "%s/__info.txt" % dirName
    file = open(filePath, 'r')
    for Line in file:
        if Line.startswith("Type"):
            file.close()
            return getShortTypeFromInfo(getValue(Line))
    return "X"

def getFullNameFromZip(file):
    fullName = "empty"

    zip = zipfile.ZipFile(file, 'r')
    filesInArhive = zip.namelist()
    for finzip in filesInArhive:
        if "bibleqt.ini" in finzip.lower():
            info = zip.read(finzip).split('\n')
            for Line in info:
                if Line.startswith("BibleName"):
                    fullName = getValue(Line)
                    zip.close()
                    return fullName
    return fullName

def getShortTypeFromInfo(longType):

    types = [
    ['bible' , 'B'],
    ['book', 'F'],
    ['dict', 'D'],
    ['strong', 'S'],
    ['comments', 'C']
    ]
    for Pair in types:
        if Pair[0] == longType:
            return Pair[1]


def downCaseBibleQtFile(path):
    print "Downcase file " + path + "..."
    (dir, file) = os.path.split(path)
    #print dir + "/bibleqt.ini"
    move_file2file(path, dir + "/bibleqt.ini")

def renameRussianNamesToEng(dir):
    print "Transliterate dir: " + os.path.abspath(dir) + "..."
    f_list = os.listdir(dir)
    for file in f_list:
        fullname =  os.path.abspath(dir + "/" + file)

        if os.path.isfile(fullname):
            #analyse of file name

            if (isinstance(fullname, str)):
                file = dir + "/" + unicode(os.path.basename(fullname), 'utf-8')
            else:
                file = dir + "/" + os.path.basename(fullname)

            newName = transliterate(file)
            #print "NewName: " + newName + "\n"
            if (newName != file):
                os.rename(os.path.abspath(file), os.path.abspath(newName))
                fixBibleQt(os.path.abspath(dir), file.replace(dir + "/", ""), newName.replace(dir + "/", ""))

            #print newName + ' OK'
        else:
            #print 'Is not a file! : ' + file
            a = 1


def inFileUseImage(path, image, encoding="   "):
    image = os.path.basename(image)
    file = open(path, 'r')
    text = ""
    if encoding == "   ":
        text = file.read().decode(getEncoding(path))
    else:
        text = file.read()
    file.close()
    if text.find(image) != -1:
        return True
    return False

def usedImageInFolder(idir):
    print "Remove unused images from path %s..." % idir
    (files, dirs) = getSubs(idir)
    images = getImagesFromDir(idir)
    workFiles = []

    for file in files:
        if not fileIsImage(file) and not fileIsFont(file) and not fileIsExe(file):
            workFiles.append(file)

    for image in images:
        value = 0
        for file in workFiles:
            if inFileUseImage(file, image):
                value += 1
                break
        if not value:
            commonscript.cleanFile(image)
            #print image
            #value = 1

def getListFilesWithAreUsedImages(f_images, f_imageDir, f_htmlDir):
    (files) = getFilesWithExt(f_htmlDir, "html")

    images = getImagesFromDir(f_imageDir)
    workFiles = []
    for image in f_images:
        for file in files:
            if inFileUseImage("%s/%s" %(f_htmlDir, file), image, "utf-8"):
                workFiles.append(file)
    return workFiles


def fixBibleQt(dir, old, new):
    fileBibleQtIni = os.path.abspath(dir + "/bibleqt.ini")

    file = open(fileBibleQtIni, 'r')
    for Line in file:
        Line = Line.decode("utf-8")
        if ("PathName = " + old).lower() in Line.lower():
            old = Line.strip().split('=')[1].lstrip().rstrip()
    file.close()

    old = "PathName = " + old
    new = "PathName = " + new
    replaceLineInFile(fileBibleQtIni, old, new)

def transliterate(string):
    capital_letters = {u'А': u'A',
                       u'Б': u'B',
                       u'В': u'V',
                       u'Г': u'G',
                       u'Д': u'D',
                       u'Е': u'E',
                       u'Ё': u'E',
                       u'З': u'Z',
                       u'И': u'I',
                       u'Й': u'Y',
                       u'К': u'K',
                       u'Л': u'L',
                       u'М': u'M',
                       u'Н': u'N',
                       u'О': u'O',
                       u'П': u'P',
                       u'Р': u'R',
                       u'С': u'S',
                       u'Т': u'T',
                       u'У': u'U',
                       u'Ф': u'F',
                       u'Х': u'H',
                       u'Ъ': u'',
                       u'Ы': u'Y',
                       u'Ь': u'',
                       u'Э': u'E',
                       u' ': u'_'}

    capital_letters_transliterated_to_multiple_letters = {u'Ж': u'Zh',
                                                          u'Ц': u'Ts',
                                                          u'Ч': u'Ch',
                                                          u'Ш': u'Sh',
                                                          u'Щ': u'Sch',
                                                          u'Ю': u'Yu',
                                                          u'Я': u'Ya',}


    lower_case_letters = {u'а': u'a',
                       u'б': u'b',
                       u'в': u'v',
                       u'г': u'g',
                       u'д': u'd',
                       u'е': u'e',
                       u'ё': u'e',
                       u'ж': u'zh',
                       u'з': u'z',
                       u'и': u'i',
                       u'й': u'y',
                       u'к': u'k',
                       u'л': u'l',
                       u'м': u'm',
                       u'н': u'n',
                       u'о': u'o',
                       u'п': u'p',
                       u'р': u'r',
                       u'с': u's',
                       u'т': u't',
                       u'у': u'u',
                       u'ф': u'f',
                       u'х': u'h',
                       u'ц': u'ts',
                       u'ч': u'ch',
                       u'ш': u'sh',
                       u'щ': u'sch',
                       u'ъ': u'',
                       u'ы': u'y',
                       u'ь': u'',
                       u'э': u'e',
                       u'ю': u'yu',
                       u'я': u'ya',
                       u' ': u'_'}

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = re.sub(ur"%s([а-я])" % cyrillic_string, ur'%s\1' % latin_string, string)

    for dictionary in (capital_letters, lower_case_letters):

        for cyrillic_string, latin_string in dictionary.iteritems():
            string = string.replace(cyrillic_string, latin_string)

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = string.replace(cyrillic_string, latin_string.upper())

    return string

def getRealNameFile(path):
    dir = os.path.split(path)[0]
    files = os.listdir(dir)
    for file in files:
        path2 = "%s/%s"  % (dir, file)
        if (path2.lower() == path.lower()):
            return "%s/%s" % (dir, file)

def getImagesFromDir(dir):
    images = []
    (files, dirs) = getSubs(dir)
    for file in files:
        if fileIsImage(file):
            images.append(u'%s' % getRealNameFile(file))
    return images

def fileIs(file, formats):
    for format in formats:
        if file.lower().endswith(format.lower()):
            return True
    return False

def fileIsImage(file):
    # add other image formats
    formats = [".gif", ".jpg", ".png"]
    return fileIs(file, formats)

def fileIsFont(file):
    formats = [".ttf"]
    return fileIs(file, formats)

def fileIsExe(file):
    formats = [".exe"]
    return fileIs(file, formats)

def getSizeFile(path):
    return os.stat(path).st_size

def addEmptyInfoToFile(path):
    file = open(path, 'w')
    file.write("Empty file detect")
    file.close()

def convertFilesToUtf(path):
    print "Convert files to utf-8..."
    path = os.path.abspath(path)
    (files, dirs) = getSubs(path)

    for name in files:
        if getSizeFile(name) == 0:
            addEmptyInfoToFile(name)

        if not fileIsImage(name) and not fileIsFont(name) and not fileIsExe(name):
            if not (convertToUtf8(name)):
                return False
    return True


def convertToUtf8(filename):
    # try to open the file and exit if some IOError occurs
    try:
        f = open(filename, 'r').read()
    except Exception:
        sys.exit(1)

    try:
        data = f.decode(getEncoding(filename))

    except Exception:
        print "TODO: ERROR!!! MOVE MODULE TO TRASH\nLastfile: " + filename
        return False

    # now get the absolute path of our filename and append .bak
    # to the end of it (for our backup file)
    fpath = os.path.abspath(filename)
    newfilename = fpath + '.bak'
    # and make our backup file with shutil
    shutil.copy(filename, newfilename)

    # and at last convert it to utf-8
    f = open(filename, 'w')
    try:
        f.write(data.encode('utf-8'))
    except Exception, e:
        print e
    finally:
        f.close()
        os.remove(newfilename)
        return True

def MakeScreening(Text):
    list = ["?", "*"]
    for elem in list:
        Text = Text.replace(elem, "\%s" % elem)
    return Text

def getEncoding(t_path):
    FileEncoding = 'utf-8'
    try:

        # get encoding from enca
        p = subprocess.Popen(configurer.CON_ENCA + " '%s'" % t_path, shell=True,
            stdout = subprocess.PIPE)
        EncaResult = p.stdout.read()

        if EncaResult < 0:
            log("enca завершил работу некорректно, ошибка")\
                    .decode('utf-8')
        else:
            # save encoding
            if (EncaResult.find("Universal transformation format 8 bits;") >= 0):
                FileEncoding = 'utf-8'
            if (EncaResult.find("Universal transformation format 16 bits;") >= 0):
                FileEncoding = 'utf-16'
            if (EncaResult.find("Universal transformation format 32 bits;") >= 0):
                FileEncoding = 'utf-32'
            if (EncaResult.find("Universal character set 2 bytes; UCS-2; BMP") >= 0):
                FileEncoding = 'ucs-2'
            if (EncaResult.find("MS-Windows code page 1251") >= 0):
                FileEncoding = "windows-1251";
            if (EncaResult.find("MS-Windows code page 1252") >= 0):
                FileEncoding = "windows-1252";
            if (EncaResult.find("MS-Windows code page 1253") >= 0):
                FileEncoding = "windows-1253";
            if (EncaResult.find("MS-Windows code page 1254") >= 0):
                FileEncoding = "windows-1254";
            if (EncaResult.find("MS-Windows code page 1255") >= 0):
                FileEncoding = "windows-1255";
            if (EncaResult.find("MS-Windows code page 1256") >= 0):
                FileEncoding = "windows-1256";
            if (EncaResult.find("MS-Windows code page 1257") >= 0):
                FileEncoding = "windows-1257";
            if (EncaResult.find("MS-Windows code page 1258") >= 0):
                FileEncoding = "windows-1258";
            if (EncaResult.find("7bit ASCII characters") >= 0):
                FileEncoding = "ascii";
            if (EncaResult.find("KOI8-R Cyrillic") >= 0):
                FileEncoding = "koi8-r";
            if (EncaResult.find("KOI8-U Cyrillic") >= 0):
                FileEncoding = "koi8-u";
            if (EncaResult.find("Unrecognized encoding") >= 0):
                #FileEncoding = "utf-8";
                FileEncoding = "Unrecognized encoding";

            #print ("Определение кодировки успешно выполнено.\n").decode('utf-8')

    except OSError, Error:
        print ("Запуск enca не удался:").decode('utf-8'), Error
    #print FileEncoding, t_path

    return FileEncoding


def pickUpFileInNLevel(dir, n):
    absDir = os.path.abspath(dir)
    #print absDir

def pickUpFileInOneLevel(dir, outputDir):
    #pickUpFileInNLevel(dir, 1)
    print "#todo"
    '''
    files, dirs = getSubs(outputDir)
    for file in files:
        (dirname, filename) = os.path.split(os.path.abspath(file))
        removeDir = dirname.split("/")[-1]

        if (removeDir != outputDir):
            newPos = dirname.replace(removeDir, "") + filename
            moveFileToFile(file, newPos)
        removeEmptyFolders(dirname)
    '''

def runConverter(command):
    #command = command.replace("python", '"C:\Program Files\Python27\python.exe"')
    print "Run converter " + command + "..."
    args = shlex.split(command)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
    return p
    #print p
    #result = p.communicate()[0]
    # todo
    #return True
    #print p


def newlineTag(Line):
    Line = Line.strip()

    if Line[(-1) * len("<br>") : ].lower() == "<br>":
        return True
    return False

def removeEmptyFolders(path):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                removeEmptyFolders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0:
        #print "Removing empty folder:", path
        os.rmdir(path)

# unzip a file
def unzipInDir(path, output):
    try:
        #os.chdir(os.path.split(output)[0])
        #output = os.path.split(output)[1]

        zfile = zipfile.ZipFile(path)
        os.mkdir(os.path.abspath(output))

        if not os.path.exists(os.path.abspath(output)):
            os.mkdir(os.path.abspath(output))


        for name in zfile.namelist():
            (dirname, filename) = os.path.split(name)
            '''
            print "name = " + name
            print "dirname = " + dirname
            print "filename = " + filename
            '''

            if filename == '':
                # directory
                if not os.path.exists(getUnicodeName(dirname)):
                    os.mkdir(output + "/" + getUnicodeName(dirname))
            else:
                # file
                #print os.path.abspath(output + "/" + getUnicodeName(filename))
                fd = open(os.path.abspath(output + "/" + getUnicodeName(filename).decode('utf-8')), 'w')
                fd.write(zfile.read(name))
                fd.close()
        zfile.close()
        return True
    except:
        return False

# unzip a file
def unzipInDir2(path, output):
    #try:

        zfile = zipfile.ZipFile(path)

        if not os.path.isdir(os.path.abspath(output)):
                os.makedirs(os.path.abspath(output))

        for name in zfile.namelist():

            (dirname, filename) = os.path.split(name)

            if dirname:
                dirPath = os.path.abspath(output) + "/" + dirname
            else:
                dirPath = os.path.abspath(output)

            if not os.path.exists(dirPath):
                os.makedirs(dirPath)

            #print dirPath + "/" + getUnicodeName(filename)
            #print name


            if filename == '':
                # directory
                if not os.path.exists(getUnicodeName(dirname)):
                    os.mkdir(output + "/" + getUnicodeName(dirname))

            else:
                # file

                testpath =  dirPath + "/" + filename.decode('utf-8')

                #fd = open(dirPath + "/" + getUnicodeName(filename), 'w')
                fd = open(testpath, 'w')
                fd.write(zfile.read(name))
                fd.close()

        zfile.close()
        return True
    #except:
    #    return False


def whatisthis(s):
    if isinstance(s, str):
        print "ordinary string"
    elif isinstance(s, unicode):
        print "unicode string"
    else:
        print "not a string"

def getUnicodeName(name):
    try:
        unicode_name = name.decode('UTF-8').encode('UTF-8')
    except:
        unicode_name = name.decode('cp866').encode('UTF-8')

    return unicode_name
#def unzip(path):
#    print "Unzip file " + path + "..."
#    unzipInDir(path, dir)
#

def getEndTag(tag):
    return tag.replace("<", "</")

def createZipFile(dir, zipName):
    z = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dir):
        for name in files:
            z.write(dir + "/" + name, name)
    z.close()

def createZip(dir):
    print "Create zip..."
    dir = os.path.abspath(dir)
    name = os.path.basename(dir) + ".zip"
    createZipFile(dir, name)

def createZipInPath(dir, output):
    zipName = os.path.basename(os.path.abspath(dir)) + ".zip"
    z = zipfile.ZipFile(output + "/" + zipName, 'w', zipfile.ZIP_DEFLATED)
    (files, dirs) = getSubs(dir)
    for name in files:
        newName = os.path.abspath(name).replace(os.path.abspath(dir) + "/", "")
        z.write(name, newName)
    z.close()

def getIdModule():
    # соединяемся с базой данных
    db = MySQLdb.connect(host="localhost", user="test", passwd="test", db="test", charset='utf8')
    # формируем курсор
    cursor = db.cursor()
    # запрос к БД
    #sql = """SELECT mail, name FROM eadres WHERE mail LIKE '%yandex.ru' LIMIT 10"""
    sql = "SELECT COUNT(*) FROM modules";
    # выполняем запрос
    cursor.execute(sql)
    # получаем результат выполнения запроса
    data =  int(cursor.fetchall()[0][0])
    db.close()
    return data

def runQuery(query):
    #print "TODO: QUERY"
    # подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
    db = MySQLdb.connect(host="localhost", user="test", passwd="test", db="test", charset='utf8')
    # формируем курсор, с помощью которого можно исполнять SQL-запросы
    cursor = db.cursor()
    # исполняем SQL-запрос
    cursor.execute(query)
    #print query.decode('utf-8')
    # применяем изменения к базе данных
    db.commit()

    # закрываем соединение с базой данных
    db.close()

def addLineInFile(filePath, inputLine):
    file = open(os.path.abspath(filePath), 'r+')
    str = ""
    for Line in file:
        str += Line + "\n"
    file.write("query:" + inputLine)
    #str += "query:" + inputLine

def replaceLineInFile(fileName, sourceText, replaceText, encoding="   "):
    file = open(fileName, 'r') #Opens the file in read-mode
    text = ""
    if encoding == "   ":
        text = file.read().decode(getEncoding(fileName)) #Reads the file and assigns the value to a variable
    else:
        text = file.read()
    file.close() #Closes the file (read session)
    file = open(fileName, 'w') #Opens the file again, this time in write-mode
    #TODO
    # надо придумать вариант, при котором 100% заменяется именно полное слово, а не часть
    # проблема в том, что я не могу проверять на "справа конец строки" или "справа"
    # ибо это может или или, а еще могут быть, наверное, другие варианты
    # Скорее всего для моего конкретного случая (Fullname = name)
    # можно проверять на этот fullname
    newText = text.replace(sourceText, replaceText, 1)
    if encoding == "   ":
        file.write(newText.encode('utf-8')) #replaces all instances of our keyword
    else:
        file.write(newText) #replaces all instances of our keyword


    # and writes the whole output when done, wiping over the old contents of the file
    file.close() #Closes the file (write session)
    #print 'All went well, the modifications are done'

def getSubs(dir):
    # get all
    dirs = []
    files = []
    for dirname, dirnames, filenames in os.walk(dir):
        dirs.append(dirname)
        for subdirname in dirnames:
            dirs.append(os.path.join(dirname, subdirname))
        for filename in filenames:
            files.append(os.path.join(dirname, filename))
    return files, dirs


def getInfoType(dir):
    file = open(os.path.abspath(dir + "/__info.txt"))
    type = "empty"
    for Line in file:
        if Line.startswith("Type"):
            type = getValue(Line)
            break
    file.close()
    return type


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
      os.kill(pid, 0)
    except OSError:
      return False
    else:
      return True

def lock(pidfile):
    if os.path.isfile(pidfile):
        pid = long(open(pidfile, 'r').read())
        if check_pid(pid):
          print "%s already exists, exiting" % pidfile
          sys.exit(0)

    pid = str(os.getpid())
    file(pidfile, 'w').write(pid)


def unlock(pidfile):
    os.unlink(pidfile)


def getFileNameInProperCase(InFileName):
    FilesList = os.listdir(os.path.dirname(InFileName))
    FileNameInLowCase = os.path.basename(InFileName).lower()
    for FileName in FilesList:
        if os.path.basename(FileName).lower() == FileNameInLowCase:
            return os.path.dirname(InFileName) + '/' + FileName
    return InFileName

'''
import MySQLdb
import string

# распаковка строки, в которой поля записаны с разделителем ";"
def unpack_line(line):
    line = string.replace(line, "'", "")
    els = string.split(line, ";")
    # выделяем имя, емейл, адрес и телефон
    fname = els[0]
    fmail = els[1]
    fadres = els[2]
    ftel = els[3]
    return fname, fmail, fadres, ftel

# подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
db = MySQLdb.connect(host="localhost", user="root", passwd="пароль", db="contacts", charset='utf8')
# формируем курсор, с помощью которого можно исполнять SQL-запросы
cursor = db.cursor()

# открываем исходный csv-файл
f = open("log", "r")
# представляем его в виде массива строк
lines = f.readlines()

for line in lines:
    # если в строе присутствует емейл (определяем по наличию "@")
    if string.find(line, "@") > -1:
        # извлекаем данные из строки
        fname, fmail, fadres, ftel = unpack_line(line)
        # подставляем эти данные в SQL-запрос
        sql = """INSERT INTO contacts(name, mail, adres, tel)
        VALUES ('%(name)s', '%(mail)s', '%(adres)s', '%(tel)s')
        """%{"name":fname, "mail":fmail, "adres":fadres, "tel":ftel}
        # исполняем SQL-запрос
        cursor.execute(sql)
        # применяем изменения к базе данных
        db.commit()

# закрываем соединение с базой данных
db.close()
# закрываем файл
f.close()
'''
