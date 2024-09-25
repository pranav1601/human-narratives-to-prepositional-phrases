import os
from docx import Document
import csv
import spacy
import re
import pandas as pd

nlp = spacy.load("en_core_web_sm")
folder_path = "input_files/"

for filename in os.listdir(folder_path):
    if filename.endswith(".docx"):
        file_path = os.path.join(folder_path, filename)
        print(f"Reading file: {filename}")
        doc = Document(file_path)
        content = []
        for para in doc.paragraphs:
            content.append(para.text.split('Mom:')[-1].strip())
        # content='\n'.join(full_text)
        print(content)
        content_editted=list(map(lambda x: x.split('Mom:')[-1].strip(),content))
        complete_sentence_list=[]
        # print(content_editted)
        for dialogue in content_editted:
            text="And, the lady tried to put that spinal tap part in four times, it took them four times. Yeah, and I had to bend over the, the pillow and I'm like, how is this not working? And by then, I was just like completely \"numb\" like to them doing everything. But they finally got it, it was fine. There was nothing complicated with our birth. It just went the way I guess all the C-sections go and she was born. And what they noticed was that her, my placenta was really small. So I very had like an inhospitable situation going on, inhospitable unit, I call myself. And then the umbilical cord was really small. It's pretty short too. So that's probably what was leading to this like gross, you know XXX her. And then the whole hydronephrosis of her kidney, which was just too much in her kidney. It actually resolved itself within the day."
            split_by_quotes = re.split(r'(\".*\")', dialogue)
            

            # Step 2: For each part, split by "and" and append to the final list
            final_split = []
            for part in split_by_quotes:
                # Step 2.1: Split by "and" for both quoted and non-quoted parts
                and_splits = re.split(r'\s+and\s+', part)
                
                # Step 2.2: Re-append 'and' to all but the last part in the split list
                for i, split in enumerate(and_splits):
                    if i >= 1:
                        final_split.append('and ' + split.strip())
                    else:
                        final_split.append(split.strip())

            # Filter out any empty strings
            final_split = [part for part in final_split if part]
            for split in final_split:


                doc = nlp(split)
                temp_sentence_list=[]
                for sent in doc.sents:
                    find_noun=1
                    start_index=0
                    end_index=-1
                    index_list=[]
                    index_len=0
                    for index,token in enumerate(sent):
                        # print(token,index)
                        if token.text==',' or token.text=='.':
                            if index_len!=0:
                                index_list[-1][1]=index+1
                                end_index=index+1
                                start_index=end_index
                            else:
                                index_list.append([start_index,index+1])
                                end_index=index+1
                                start_index=end_index
                        elif find_noun==1:
                            if token.pos_ in ["NOUN", "PROPN", "PRON"]:
                                # print(token.text)
                                end_index=index
                                index_list.append([start_index,end_index])
                                index_len+=1
                                start_index=index
                                find_noun=0
                        else:
                            if token.pos_ in ["VERB", "AUX"]:
                                # print(token.text)
                                find_noun=1
                    index_list.append([start_index,sent.end])
                    sentence_list=list(map(lambda x: str(sent[x[0]:x[1]]),index_list))
                    temp_sentence_list.extend(sentence_list)
                sentence_formed=' / '.join(temp_sentence_list)
                complete_sentence_list.append(sentence_formed)
        

        cleaned_texts = list(map(lambda text: re.sub(r'( / )+', ' / ', text), complete_sentence_list))

        cleaned_texts_strings=[]
        for dialogue in cleaned_texts:
            cleaned_texts_string=[]
            propositional_split=dialogue.split(' / ')
            new_split=[]
            temp_split=[]
            length_propositional_split=len(propositional_split)
            to_remove_indices=[]
            for part in propositional_split:
                if len(part)!=0:
                    if (len(part.split())==1 or len(part.split())==2) and part[-1]!='.' and part[0]!='"' and part[-1]!='"':
                        temp_split.append(part.encode().decode('unicode_escape').strip())
                    else:
                        if temp_split:
                            new_part = ' '.join(temp_split + [part])
                            new_split.append(new_part.encode().decode('unicode_escape').strip())
                            temp_split = []
                        else:
                            new_split.append(part.encode().decode('unicode_escape').strip())
            if temp_split:
                new_split += temp_split
            
            cleaned_texts_strings.extend(new_split)
                            


        print(cleaned_texts_strings)
        df_cleaned_texts_strings=pd.DataFrame(cleaned_texts_strings,columns=["PHRASES"])
        df_cleaned_texts_strings=df_cleaned_texts_strings.dropna()
        df_cleaned_texts_strings.to_csv('outputs/'+filename+'_output.tsv',sep="\t",quoting=csv.QUOTE_NONE,escapechar="\\",index=False)
        



