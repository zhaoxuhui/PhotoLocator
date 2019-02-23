# coding=utf-8
from PIL import Image
from PIL.ExifTags import TAGS
import os


def findAllFiles(root_dir, filter):
    """
    遍历搜索文件

    :param root_dir:搜索目录
    :param filter: 搜索文件类型
    :return: 路径、文件名、路径+文件名
    """
    print("Finding files ends with \'" + filter + "\' ...")
    separator = os.path.sep
    paths = []
    names = []
    files = []
    # 遍历
    for parent, dirname, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(filter):
                paths.append(parent + separator)
                names.append(filename)
    for i in range(paths.__len__()):
        files.append(paths[i] + names[i])
    print (names.__len__().__str__() + " files have been found.")
    paths.sort()
    names.sort()
    files.sort()
    return paths, names, files


def get_exif_data(fname):
    """
    获取EXIF信息

    :param fname: 影像文件路径
    :return: 字典类型的EXIF信息
    """
    ret = {}
    try:
        img = Image.open(fname)
        if hasattr(img, '_getexif'):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
            else:
                ret = 'no exif'
    except IOError:
        print 'IOERROR ' + fname
    return ret


if __name__ == '__main__':
    directory = raw_input("Input directory of images('.' as default):\n")
    file_type = raw_input("Input image type('.jpg' as default):\n")

    if directory is "":
        directory = "."
    if file_type is "":
        file_type = ".jpg"

    paths, names, files = findAllFiles(directory, file_type)
    photo_info = []
    for i in range(files.__len__()):
        print "reading ", (i + 1), "/", files.__len__()
        exif = get_exif_data(files[i])
        if exif != "no exif":

            if exif.get('FocalLength') is not None:
                focalLength = exif.get('FocalLength')[0] * 1.0 / exif.get('FocalLength')[1]
            else:
                focalLength = 0

            if exif.get("ISOSpeedRatings") is not None:
                iso = exif.get("ISOSpeedRatings")
            else:
                iso = 0

            if exif.get("Model") is not None:
                model = exif.get("Model")
            else:
                model = "default"

            if exif.get("ShutterSpeedValue") is not None:
                if exif.get("ShutterSpeedValue")[0] == 0:
                    shutter = (exif.get("ShutterSpeedValue")[0] * 1.0).__str__()
                else:
                    shutter = "1/" + int(
                        1000 / (exif.get("ShutterSpeedValue")[0] * 1.0 /
                                exif.get("ShutterSpeedValue")[1])).__str__()
            else:
                shutter = "1/0"

            time_info = exif.get("DateTime")

            if exif.has_key('GPSInfo'):
                info = exif.get('GPSInfo')
                if info.has_key(1) and info.has_key(3):
                    lat = info[2]
                    lon = info[4]
                    lat_deg = lat[0][0] * 1.0 / lat[0][1]
                    lat_min = lat[1][0] * 1.0 / lat[1][1]
                    lat_sec = lat[2][0] * 1.0 / lat[2][1]
                    lon_deg = lon[0][0] * 1.0 / lon[0][1]
                    lon_min = lon[1][0] * 1.0 / lon[1][1]
                    lon_sec = lon[2][0] * 1.0 / lon[2][1]
                    lat_decimal = lat_deg + lat_min / 60.0 + lat_sec / 3600.0
                    lon_decimal = lon_deg + lon_min / 60.0 + lon_sec / 2600.0
                    if info[1] is u'S':
                        lat_decimal = -lat_decimal
                    if info[3] is u'W':
                        lon_decimal = -lon_decimal
                    photo_info.append((focalLength, iso, model, shutter, time_info, (lat_decimal, lon_decimal)))
                else:
                    photo_info.append("no info")
            else:
                photo_info.append("no info")

    mean_lon = 0
    mean_lat = 0
    counter = 0
    placemarks = []

    for i in range(photo_info.__len__()):
        if photo_info[i] is not "no info":
            line1 = "\t\t\t<Placemark>\n"
            line2 = "\t\t\t\t<name>" + names[i] + "</name>\n"
            line3 = "\t\t\t\t<description>\n"
            line4 = "\t\t\t\t<img style=\"max-width:500px;\" src=\"file:///" + files[i] + "\"></img>\n"
            line5 = "\t\t\t\tISO:" + photo_info[i][1].__str__() + \
                    " ShutterSpeed:" + photo_info[i][3].__str__() + \
                    " FocalLength:" + photo_info[i][0].__str__() + \
                    "<br />Datetime:" + photo_info[i][4] + \
                    " Camera:" + photo_info[i][2] + "\n"
            line6 = "\t\t\t\t</description>\n"
            line7 = "\t\t\t\t<Point>\n"
            line8 = "\t\t\t\t\t<coordinates>" + photo_info[i][5][1].__str__() + "," + photo_info[i][5][
                0].__str__() + ",0</coordinates>\n"
            line9 = "\t\t\t\t</Point>\n"
            line10 = "\t\t\t</Placemark>\n"

            counter += 1
            mean_lon = mean_lon + photo_info[i][5][1]
            mean_lat = mean_lat + photo_info[i][5][0]

            item = line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10
            placemarks.append(item)

    mean_lon = mean_lon / counter
    mean_lat = mean_lat / counter

    photos = open(directory + os.path.sep + "photos.kml", 'w+')
    photos.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    photos.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
    photos.write("\t<Document>\n")
    photos.write("\t\t<name>Photos</name>\n")
    photos.write("\t\t<open>1</open>\n")
    photos.write("\t\t<description>KML file created by PhotoLocator.</description>\n")
    photos.write("\t\t<Folder>\n")
    photos.write("\t\t\t<name>Placemarks</name>\n")
    photos.write("\t\t\t<description>Your photos with geo-info are listed here.</description>\n")
    photos.write("\t\t\t<LookAt>\n")
    photos.write("\t\t\t\t<longitude>" + mean_lon.__str__() + "</longitude>\n")
    photos.write("\t\t\t\t<latitude>" + mean_lat.__str__() + "</latitude>\n")
    photos.write("\t\t\t\t<altitude>0</altitude>\n")
    photos.write("\t\t\t\t<tilt>10</tilt>\n")
    photos.write("\t\t\t</LookAt>\n")
    for item in placemarks:
        photos.write(item)
    photos.write("\t\t</Folder>\n")
    photos.write("\t</Document>\n")
    photos.write("</kml>")

    print "Result has been saved at:", directory + os.path.sep + "photos.kml"
    photos.close()
