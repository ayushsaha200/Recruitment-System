import subprocess
from os import listdir
from os.path import isfile, join
from docx import Document
import codecs

def file_operation():
    mypath = 'C:\Users\Ayush\Desktop\Ayush\VIT\Sem\NLP\Project\content\Resumes'
    list_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for k in range(len(list_files)):
        document = Document(list_files[k])
        print(document.paragraphs)