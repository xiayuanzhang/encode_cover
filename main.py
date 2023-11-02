import sys,os
import fnmatch
import chardet
import codecs
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from PyQt5.QtCore import Qt

from widget import Ui_Form
import datetime
import warnings

# 忽略 DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 适应高DPI设备
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
# 解决图片在不同分辨率显示模糊问题
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# 获取使用空格间隔的字符串,切片列表
def split_extensions(extensions_string):
    return extensions_string.split()


# 正则列表查找root_folder中指定后缀的文件
def find_files_with_patterns(root_folder, patterns):
    matching_files = []

    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern):
                    matching_files.append(os.path.join(foldername, filename))

    return matching_files


# 获取文件编码类型
def detect_file_encoding(file_path):
    if not os.path.exists(file_path):
        return ""
    if os.path.getsize(file_path) == 0:
        return ""
    with open(file_path, 'rb') as file:
        rawdata = file.read()
        result = chardet.detect(rawdata)
    return result['encoding']


# 编码格式表 https://docs.python.org/3/library/codecs.html#standard-encodings
def convert_file_encoding(input_file_path, output_file_path, target_encoding):
    source_encoding = detect_file_encoding(input_file_path)
    if not source_encoding:
        return -1, " (err, file abnormal)"
    try:
        with codecs.open(input_file_path, 'r', encoding=source_encoding, errors='strict') as input_file:
            content = input_file.read()
    except UnicodeDecodeError:
        return -1, " (open err , encoding = " + source_encoding + ")"
    try:
        content.encode(target_encoding)
    except UnicodeEncodeError:
        return -1, " (encode err, encoding = " + target_encoding + ")"

    with codecs.open(output_file_path, 'w', encoding=target_encoding, errors='strict') as output_file:
        output_file.write(content)
    return 0, " (" + source_encoding + " --> " + target_encoding + ")"


class Window(QWidget, Ui_Form):
    def __init__(self):
        super(QWidget, self).__init__()
        self.setupUi(self)
        self.cover.clicked.connect(self.on_cover_button)
        self.fileDirBut.clicked.connect(self.on_filedir_choose_button)

    def on_cover_button(self):
        self.output.clear()
        current_time = datetime.datetime.now()
        time_string = current_time.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间为字符串
        self.output.append(time_string)

        folder_path = self.fileDir.text()
        extensions_string = self.fileFilter.text()
        extensions = split_extensions(extensions_string)
        matching_files = find_files_with_patterns(folder_path, extensions)
        target_encoding = self.encodeing.currentText()
        err_count = 0
        total_count = 0;
        if matching_files:
            for file_path in matching_files:
                res_value, res_str = convert_file_encoding(file_path, file_path, target_encoding)
                if res_value == -1:
                    err_count += 1
                total_count += 1
                self.output.append(file_path + res_str)
        self.output.append("")
        self.output.append("cover over, total_count = %d ,err_count = %d" % (total_count, err_count))
        self.output.append("")

    def on_filedir_choose_button(self):
        path = QFileDialog.getExistingDirectory(self, "选取指定文件夹", os.path.expanduser("~/Desktop"))
        if path:
            self.fileDir.setText(path)


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    sys.exit(app.exec())

