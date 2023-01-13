from multiprocessing.managers import DictProxy
import os
import array as arr
from collections import OrderedDict
from pickletools import string1 #converting an object in the memory to a byte stream that can be stored as a binary file on disk
import docx2txt
from prettytable import PrettyTable #create relational tables
from sklearn.feature_extraction.text import CountVectorizer  #convert a collection of text documents to a vector of term/token counts
from sklearn.metrics.pairwise import cosine_similarity #similarity between two non zero vectors
import codecs
import webbrowser 

job_desc_docx_path = "content/job_desc.docx"
#resume_docx_path = "/content/applicant_resume.docx"
APP_FOLDER = 'content/resumes'

f=open('cos_sim.html','w')
#the html code which will go in the file cos_sim.html
html_template = """<html>
<head>
<title>Cosine Similarity</title>
<link rel = "stylesheet" href="p.css">
</head>
<body>
"""
f.write(html_template)

totalFiles=0
totalDir=0
for base,dirs,files in os.walk(APP_FOLDER):
    print('Searching in : ',base)
    str1='Cosine Similarity'
    f.write(str1)
    for directories in dirs:
        totalDir+=1
    for Files in files:
        totalFiles+=1

def ResumeAnalyzer(fileObject):
    match_percentage=[0]*totalFiles
    files=[0]*totalFiles
    i=0

    resume_folder_path="content/resumes"
    for filename in os.listdir(resume_folder_path):
        f=os.path.join(resume_folder_path,filename)
        if os.path.isfile(f):
            applicant_resume_docx=f
            files[i]=applicant_resume_docx
            job_description_docx=job_desc_docx_path
            result1=docx2txt.process(applicant_resume_docx)
            result2=docx2txt.process(job_desc_docx_path)
            text=[result1,result2]
            cv=CountVectorizer()
            #used to transform a given text into a vector on the basis of the frequency of each word that occurs in the entire text

            count_matrix=cv.fit_transform(text)
            match_percentage=cosine_similarity(count_matrix)[0][1]*100
            match_percentage=round(match_percentage,2)
            match_percentage[i]=match_percentage
            i=i+1

    dictionary=dict(files, match_percentage)
    sorted_values=sorted(dictionary.values())
    sorted_dict={}
    for i in sorted_values:
        for k in dictionary.keys():
            if dictionary[k]==i:
                sorted_dict[k]=dictionary[k]
                break
    
    final_dict=dict(OrderedDict(reversed(list(sorted_dict.items()))))
    final_list=list(final_dict.items())
    x=PrettyTable()
    x.field_names=["Resume","Score"]

    for i in range(len(final_list)):
        file=str(final_list[i][0])
        resume1=file.replace('content/resumes','')
        resume=resume1.replace('.docx','')
        x.add_row([resume,final_list[i][1]])
    print(x)
    str2=x.get_html_string()
    fileObject.write(str2)

ResumeAnalyzer(f)

html_template="""</body></html>"""
f.write(html_template)
f.close()
webbrowser.open('cos_sim.html')