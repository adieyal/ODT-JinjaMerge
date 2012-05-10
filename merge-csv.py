import csv,cgi
import os
import shutil
import args
import sys
from jinja2 import FileSystemLoader,Environment, Template
import tempfile
import zipfile
from DocumentConverter import DocumentConverter

class ODTZip(object):
    def __init__(self, filename):
        self.filename = filename
        self.zip = zipfile.ZipFile(filename, "a")
        if not "content.xml" in self.zip.namelist():
            raise Exception("Expected to find content.xml in template file but couldn't.")

    def get_content_xml(self):
        return self.zip.open("content.xml").read()

    def write_content_xml(self, xml):
        self.zip.writestr("content.xml", xml)

    def close(self):
        #TODO it would be great to automatically flush on write
        self.zip.close()

def mail_merge(template, row_dict):
    fn_user = row_dict["filename"]
    shutil.copyfile(fn_template, fn_user)

    odtzip = ODTZip(fn_user)

    template = Template(odtzip.get_content_xml())

    new_dict = {key : unicode(cgi.escape(row_dict[key]), errors='ignore') for key in row_dict}

    output = template.render(user=new_dict)

    odtzip.write_content_xml(output)
    odtzip.close()

def main(fn_template, fn_data):
    fp_data = open(fn_data)
    reader = csv.DictReader(open(fn_data))

    users = list(reader)
    converter = DocumentConverter()

    for user in users:
        user["filename"] = "%s_%s.odt" % (user["first_name"], user["last_name"])
        user["filename_pdf"] = "%s_%s.pdf" % (user["first_name"], user["last_name"])
        mail_merge(fn_template, user)

        converter.convert(user["filename"], user["filename_pdf"])

def check_file_input(flag_name):
    if not flag_name in pairs:
        raise Exception("Expected %s given as an argument" % flag_name)
    if len(pairs[flag_name]) != 1 or not os.path.exists(pairs[flag_name][0]):
        raise Exception("Could not find file")

    return pairs[flag_name][0]

if __name__ == "__main__":
    pairs = args.grouped
    fn_template = check_file_input("--template")
    fn_data = check_file_input("--data")
        
    main(fn_template, fn_data)
