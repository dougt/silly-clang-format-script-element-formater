from HTMLParser import HTMLParser
import os
from subprocess import Popen, PIPE
import sys

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.processing_script_element = False
        self.current_open_offset = 0
        self.current_formated_data = ""
        self.replacement_data = []

    def handle_starttag(self, tag, attrs):
        if tag != "script":
            return

        if attrs != []:
            return

        self.processing_script_element = True
        self.current_open_offset = self.getpos()[0] + 1

    def handle_endtag(self, tag):
        if tag != "script":
            return

        if self.processing_script_element == False:
            return

        self.processing_script_element = False
        self.replacement_data.append((self.current_open_offset, self.getpos()[0] - 1, self.current_formated_data))

    def handle_data(self, data):
        if self.processing_script_element == False:
            return

        p = Popen(["clang-format", "-assume-filename=file.js"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self.current_formated_data = p.communicate(data)[0]
        if p.returncode != 0:
            self.processing_script_element = False

def process_file(filename):
    parser = MyHTMLParser()

    # To keep line numbers, we read one line in at a time.
    content = ""
    file = open(filename, "r")
    for line in file:
        parser.feed(line)
        content = content + line
    file.close()

    file = open(filename, "w")
    line_count = 0
    skip_count = 0
    for line in content.splitlines(True):
        line_count = line_count + 1

        if skip_count > 0:
            skip_count = skip_count - 1
            continue;

        if (len(parser.replacement_data) > 0):
            if line_count == int(parser.replacement_data[0][0]):
                replacement_data = parser.replacement_data.pop(0)
                skip_count = int(replacement_data[1]) - int(replacement_data[0])
                file.writelines(replacement_data[2].lstrip())
                continue

        file.write(line)
    file.close()


if __name__ == "__main__":

    if sys.argv < 2:
        print('Please specify a filename.')
        exit(-1)

    filename = sys.argv[1]
    print(filename)

    if os.path.isfile(filename):
        process_file(filename)
        exit(0)
    else:
        for i in os.listdir(filename):
            f = os.path.join(filename, i)
            if os.path.isfile(f):
                process_file(f)
        exit (0)

