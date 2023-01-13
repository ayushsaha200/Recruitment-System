import os
from os import listdir
from os.path import isfile, join
import math
import PyPDF2
from collections import Counter
import spacy
import en_core_web_sm;
from io import StringIO
import pandas as pd

#Load English tokenizer, tagger, parser, NER and word vectors
nlp=spacy.load("en_core_web_sm")
from spacy.matcher import PhraseMatcher

#Functions to read resumes from the folder (one at a time)
mypath="resumes"
onlyfiles=[os.path.join(mypath,f) for f in os.listdir(mypath) if
os.path.isfile(os.path.join(mypath,f))]

def pdftotext(file):
    fileReader=PyPDF2.PdfFileReader(open(file,'rb'))
    countpage=fileReader.getNumPages()
    count=0
    text=[]
    while count<countpage:
        pageObj=fileReader.getPage(count)
        count+=1
        t=pageObj.extractText()
        text.append(t)
    return text

#functions to read resumes ends

#function that does phrase matching and builds a candidate profile

def resume_parse(file,idx):
    text=pdftotext(file)
    text=str(text)
    text=text.replace("\\n","")
    text=text.lower()
    #below is the csv where we have all the keywords (customizable)

    keyword_dict=pd.read_csv('nlp-edit.csv')
    stats_tokens=[nlp(text) for text in 
keyword_dict['Statistics'].dropna(axis=0)]
    NLP_tokens=[nlp(text) for text in
keyword_dict['NLP'].dropna(axis=0)]
    ML_tokens=[nlp(text) for text in keyword_dict['Machine Learning'].dropna(axis=0)]
    DL_tokens = [nlp(text) for text in keyword_dict['Deep Learning'].dropna(axis=0)]
    R_tokens = [nlp(text) for text in keyword_dict['R Language'].dropna(axis=0)]
    python_tokens = [nlp(text) for text in keyword_dict['Python Language'].dropna(axis=0)]
    Data_Engineering_tokens = [nlp(text) for text in keyword_dict['Data Engineering'].dropna(axis=0)]
    WebDev_tokens = [nlp(text) for text in keyword_dict['Web Development'].dropna(axis=0)]
    management_tokens = [nlp(text) for text in
keyword_dict['Management'].dropna(axis=0)]
    finance_tokens = [nlp(text) for text in
keyword_dict['Finance'].dropna(axis=0)]
    engineering_tokens = [nlp(text) for text in
keyword_dict['Engineering'].dropna(axis=0)]

    matcher=PhraseMatcher(nlp.vocab)
    matcher.add('Stats',None,*stats_tokens)
    matcher.add('NLP', None, *NLP_tokens)
    matcher.add('ML', None, *ML_tokens)
    matcher.add('DL', None, *DL_tokens)
    matcher.add('R', None, *R_tokens)
    matcher.add('Python', None, *python_tokens)
    matcher.add('DE', None, *Data_Engineering_tokens)
    matcher.add('WebDev', None, *WebDev_tokens)
    matcher.add('Mgt', None, *management_tokens)
    matcher.add('Fin', None, *finance_tokens)
    matcher.add('Engg', None, *engineering_tokens)
    doc=nlp(text)

    d=[]
    score=[]
    matches=matcher(doc)
    for match_id, start, end in matches:
        rule_id=nlp.vocab.strings[match_id]
        span=doc[start: end]
        d.append((rule_id,span.text))
    keywords="\n".join(f'{i[0]} {i[1]} ({j})' for i,j in 
    Counter(d).items())

    df = pd.read_csv(StringIO(keywords), names=['Keywords_List']) #read doc as keyword_lsit 1 col
    df1 = pd.DataFrame(df.Keywords_List.str.split(' ', 1).tolist(),columns=['Subject', 'Keyword']) #splits df into 2 colums
    df2 = pd.DataFrame(df1.Keyword.str.split('(', 1).tolist(),columns=['Keyword', 'Count']) #splits df1 and gets count of keywords
    df3 = pd.concat([df1['Subject'], df2['Keyword'], df2['Count']],axis=1) #concars df1 and df2 so 3columsn
    df3['Count'] = df3['Count'].apply(lambda x: x.rstrip(")")) #removes trailing spaces
    base=os.path.basename(file)
    filename=os.path.splitext(base)[0] #print candidate names from the flie name
    name=filename.split('_')
    name2=name[0]
    name2=name2.lower()

    #converting string to dataframe
    name3 = pd.read_csv(StringIO(name2),names=['Candidate Name'])
    dataf = pd.concat([name3['Candidate Name'], df3['Subject'], df3['Keyword'], df3['Count']], axis=1)
    dataf=['Candidate Name'].fillna(dataf['Candidate Name'].iloc[0], inplace=True)

    #Calculating Scoring of candidate
    tot_sum=df3['Count'].sum()
    score.append((dataf['Candidate Name'][0], tot_sum))
    return (dataf)

#Assuming we are shortlisting for AI Profile
recruiter_score=dict()

def recruiter_input():
    global recruiter_score

    #get input values from the recruiter
    print("\n**********RECRUITER MENU**********")
    print('Candidate Shortlisting & Profile Build')
    de=int(input('\nEnter Data Engineering weightage: '))
    dl=int(input('Enter Deep Learning engineering weightage: '))
    ml=int(input('Enter Machine Learning weightage: '))
    nlp=int(input('Enter Natural Language Processing weightage: '))
    py=int(input('Enter Python weightage: '))
    r=int(input('Enter R weightage: '))
    st=int(input('Enter Statistics weightage: '))
    wd=int(input('Enter Web Development weightage: '))
    mg=int(input('Enter Management weightage: '))
    fin=int(input('Enter Finance weightage: '))
    eg=int(input('Enter Engineering weightage: '))

    recruiter_score["DE"] = de
    recruiter_score["DL"] = dl
    recruiter_score["ML"] = ml
    recruiter_score["NLP"] = nlp
    recruiter_score["Python"] = py
    recruiter_score["R"] = r
    recruiter_score["Stats"] = st
    recruiter_score["WebDev"] = wd
    recruiter_score["Mgt"] = mg
    recruiter_score["Fin"] = fin
    recruiter_score["Engg"] = eg

def score_calc():
    global recruiter_score, score, shortlist2
    mm=[]
    col=[]
    for i in shortlist2.columns:
        col.append(i)
    name=""
    for i in range(len(shortlist2)):
        name=shortlist2.iloc[i,0]
        subsum=0
        for j in range(1,len(shortlist2.columns)):
            num1 = shortlist2.iloc[i, j]
            num2 = recruiter_score.get(col[j])
            subsum += int(num1)*num2
            """A scoring mechanism is used which helps us to filter out the candidates for the profile we have made the application for, by giving more weight to that particular field and assigning less weight to the others. Eg. For shortlisting candidates for an AI profile, more weightage is given to fields like Deep Learning, NLP, Machine learning compared to Statistics and Web Development"""
            mm.append((name,subsum))
            score=mm


# Tuple Sorting Function
#sort in descending order
def Sort(tup):
    # getting length of list of tuples
    lst = len(tup)
    for i in range(0, lst):
        for j in range(0, lst - i - 1):
            if (tup[j][1] > tup[j + 1][1]):
                temp = tup[j]
                tup[j] = tup[j + 1]
                tup[j + 1] = temp
        return tup

from prettytable import PrettyTable
#printing cand name along with score
def Show_Shortlist(show):
    global score, selected
    num_sel = math.ceil(len(score) / show)
    selected = []
    Sort(score)
    j = len(score) - 1
    while (j > 0 and num_sel > 0):
        selected.append((score[j][0], score[j][1]))
        num_sel -= 1
        j -= 1
    t = PrettyTable(['Name', 'Score'])
    for i in range(len(selected)):
        t.add_row([selected[i][0], selected[i][1]])
    print(t)

# code to count words under each category and visulaize it through Matplotlib
def data_plot():
    global shortlist2, shortlist 
    shortlist2 = shortlist['Keyword'].groupby([shortlist['Candidate Name'], shortlist['Subject']]).count().unstack() 
    shortlist2.reset_index(inplace=True)
    shortlist2.fillna(0, inplace=True)
    new_data = shortlist2.iloc[:, 1:]

    #Python iloc() function enables us to select a particular cell of the dataset, that is, it helps us select a value that belongs to a particular row or column from a set of values of a data frame or dataset.
    new_data.index = shortlist2['Candidate Name']
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10})
    ax = new_data.plot.barh(title="Resume keywords by category", legend=False, figsize=(25, 7), stacked=True)
    labels = []

    for j in new_data.columns:
        for i in new_data.index:
            label = str(j) + ": " + str(new_data.loc[i][j])
            labels.append(label)
    patches = ax.patches
    for label, rect in zip(labels, patches):
        width = rect.get_width()
        if width > 0:
            x = rect.get_x()
            y = rect.get_y()
            height = rect.get_height()
            ax.text(x + width / 2., y + height / 2., label, ha='center', va='center')
    plt.show()


shortlist = pd.DataFrame() #all candi resume parse
shortlist2 = pd.DataFrame() #actual shortlist reused fro selection
score = []
selected = []

def main():
    global shortlist, shortlist2, recruiter_score
    i = 0
    while i < len(onlyfiles):
        file = onlyfiles[i]
        dat = resume_parse(file, i)
        shortlist = shortlist.append(dat)
        i += 1
    recruiter_input()
    data_plot()
    score_calc()

    print("Shortlist 1-Candidate Names with Score : ")
    Show_Shortlist(1)
    print("Selected Candidates :")
    Show_Shortlist(100)

if __name__ == '__main__':
    main()


