#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018 <boutin_arnaud@hotmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os, codecs, subprocess

from core.utils.G2PUtils import G2PTools
from core import LANG, NGRAM_COUNT


class Tools():
    
    def __init__(self):
        self.G2PTools = G2PTools()
    
    def write_file(self, path, lines):
        current_dir = os.path.dirname(__file__)
        file_location = os.path.join(current_dir, path)
        file_write = codecs.open( file_location, 'w', 'utf8')
        for l in lines:
            try:
                l_lower = self.cleanString(l) + "\n"
                file_write.write(l_lower)
            except Exception as e:
                print(l + "  " + e.__str__())    
        file_write.close()

    def read_file(self, path):
        current_dir = os.path.dirname(__file__)
        file_location = os.path.join(current_dir, path)
        file_read = codecs.open(file_location, 'r', 'utf8')
        content = file_read.readlines() 
        file_read.close()    
        return content
    
    def formatWordToDIC(self, word, vocal):
        lines  = []
        for index, grapheme in enumerate(vocal) :
            if index == 0: 
                lines.append(word + " " + grapheme.grapheme)
            else :
                lines.append(word + "(" + str(index + 1)  + ")" + " " + grapheme.grapheme)    
        return lines        
    
    def compare(self, string1, string2):
        return self.cleanString(string1) == self.cleanString(string2)

    def cleanString(self, s):
        return s.strip().lower().rstrip('\n').rstrip('\r').rstrip('!').rstrip('?').rstrip('.').rstrip('/').rstrip(',').rstrip(':')

    
    """
        déduit la liste des mots a partir d'une liste de phrases
    """
    def buildVocab(self, lines):
        listWords= []
        for line in lines :
            list_word_line = line.split(' ')
            for word in list_word_line:
                w = self.cleanString(word)
                if w not in listWords :
                    listWords.append(w)
        
        return listWords
        
    def buildVocabFile(self, input_path, output_path):
        lines = self.read_file(input_path)
        listWords= self.buildVocab(lines)
        self.write_file(output_path, listWords)
    
    def buildGraphemeToPhoneme(self, list_word):
        current_dir = os.path.dirname(__file__)
        dic_general_fr_path = '../../resources/fr/frenchWords62K.dic'
        dic_general_fr_en_path = '../../resources/fr/model_fr_en.dic'
        dic_general_en_path = '../../resources/en/cmudict.hub4.06d.dic'
        dic_general_es_path = '../../resources/es/voxforge_es_sphinx.dic'
        dic_spec_path    = '../../resources/fr/model_vocal/topi.dic'
        dictionaire = []

        dic_general_location = os.path.join(current_dir, dic_general_fr_path)
        content_dic_general = self.read_file(dic_general_location)

        dic_spec_location = os.path.join(current_dir, dic_spec_path)
        content_spec_general = self.read_file(dic_spec_location)
        
        dic_general_fr_en_location = os.path.join(current_dir, dic_general_fr_en_path)
        dic_general_fr_en_general = self.read_file(dic_general_fr_en_location)

        list_words_not_find = self.findListWordsInDic(content_spec_general, dictionaire, list_word)
       
        if len(list_words_not_find) > 0:
            a = self.findListWordsInDic(content_dic_general, dictionaire, list_words_not_find)
            b = self.findListWordsInDic(dic_general_fr_en_general, dictionaire, list_words_not_find)
            list_words_not_find = list(set(a) & set(b))
        
        if len(list_words_not_find) > 0 :
            for w in list_words_not_find :
                print(w + " not find!!!")
            
            dictionaire.extend(self.launchG2PTools(list_words_not_find))
        
        return sorted(dictionaire)  

    def launchG2PTools(self, list_word):
        input_file_path  = "../../tmp/input_mots_to_gp2"
        ouput_file_path  = "../../tmp/output_mots_to_gp2"
        
        current_dir = os.path.dirname(__file__)
        file_input_location = os.path.join(current_dir, input_file_path)
        self.write_file( file_input_location, list_word)
        
        self.G2PTools.decode()
        
        file_ouput_location = os.path.join(current_dir, ouput_file_path)
        content = self.read_file(file_ouput_location)
        return content


    def findListWordsInDic(self, content_dic, dictionaire, list_words) :
        list_words_find = []
        for line in content_dic:
            list_ = line.split(' ', 1)
            mot_general = list_[0].split('(')[0] if '(' in list_[0] else list_[0]
            mot_general_clean = self.cleanString(mot_general)
            for word in list_words :
                word_clean = self.cleanString(word)
                if word_clean == '(2012)' or word_clean == '(2013)':
                    list_words_find.append(word)
                if mot_general_clean == word_clean :    
                    dictionaire.append(line)
                    if word not in list_words_find : 
                        list_words_find.append(word)    
                
        list_words_not_find = [x for x in list_words if x not in list_words_find]
        return list_words_not_find
    
    """
        Construit le language model statistic
    """
    def buildStatisticLanguageModel(self, phrase):
        """
        cd /home/nono/workspace/clientComponent/resources
        ./ngram-count -wbdiscount -interpolate -text model.txt -lm modelLm.lm  -write-vocab text.vocab -debug 2      
        sphinx_lm_convert -i modelLm.lm -o modelLm.lm.bin
        """
        current_dir = os.path.dirname(__file__)
        text_path = "../../resources/" + LANG + "/model_phrase"
        self.write_file(text_path, phrase)

        text_location = os.path.join(current_dir, text_path)
        lm_path = "../../resources/" + LANG + "/topi.lm"
        lm_location = os.path.join(current_dir, lm_path)
        vocab_path ="../../resources/" + LANG + "/text.vocab"
        vocab_location = os.path.join(current_dir, vocab_path)
        
        ngram_count = os.path.join(current_dir, "../../resources/" + NGRAM_COUNT)
        command = ngram_count + " -wbdiscount -interpolate -text "+ text_location+ " -lm " + lm_location + "  -write-vocab "+vocab_location+" -debug 2"
        os.system(command)
        lm_bin_path = "../../resources/"+ LANG+"/model_vocal/topi.lm.bin"
        lm_bin_location = os.path.join(current_dir, lm_bin_path)
        command = "sphinx_lm_convert -i "+lm_location+" -o " + lm_bin_location
        os.system(command)        
    
    
    """
        Permet de construire les 2 fichiers vocab.grapheme et vocab.phoneme a partir d'un dictionnaire
    """
    def GraphemePhoneme(self):
        current_dir = os.path.dirname(__file__)
        script = '../../model_vocal/frenchWords62K.dic'
        graphemeFile = '../../model_vocal/vocab.grapheme'
        phonemeFile = '../../model_vocal/vocab.phoneme'
        
        file_location = os.path.join(current_dir, script)

        file_encoding = subprocess.getoutput('file -b --mime-encoding %s' % file_location)
        file_stream = codecs.open(file_location, 'r', file_encoding)
        content = file_stream.readlines() 
            
        list_phoneme = []
        list_grapheme = []    
        for line in content :
            list_ = line.split(' ')
            for c in list_[0] :
                if c not in list_grapheme :
                    list_grapheme.append(c)
                    print(c)
            del list_[0]
            for phoneme in list_ :
                if "\n" in phoneme:
                    phoneme = phoneme.rstrip('\n')
                    
                if phoneme not in list_phoneme :
                    list_phoneme.append(phoneme)
                    
        for p in list_phoneme :
            print(p)   
                    
        file_grapheme_output = codecs.open(os.path.join(current_dir, graphemeFile), 'w', 'utf-8')
        file_phoneme_output = codecs.open(os.path.join(current_dir, phonemeFile), 'w', 'utf-8')
        
        file_grapheme_output.write("_PAD\n_GO\n_EOS\n_UNK\n")
        file_phoneme_output.write("_PAD\n_GO\n_EOS\n_UNK\n")
        
        for l in list_grapheme:
            file_grapheme_output.write(l+"\n")
        
        for l in list_phoneme:
            file_phoneme_output.write(l+"\n")
        
        file_stream.close()
        file_grapheme_output.close()
        file_phoneme_output.close()           
