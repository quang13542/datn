import pandas as pd
import ast
import pickle
import re

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, sentence):
        node = self.root
        sentence = sentence.lower()
        words = sentence.split()
        for word in words:
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
        node.is_end_of_word = True

    def search(self, sentence):
        node = self.root
        sentence = sentence.lower()
        words = sentence.split()
        for word in words:
            for char in word:
                if char not in node.children:
                    return 'not in trie'
                node = node.children[char]
        return node.is_end_of_word

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.root, file)

    @staticmethod
    def load_from_file(filename):
        trie = Trie()
        with open(filename, 'rb') as file:
            trie.root = pickle.load(file)
        return trie

def search_in_trie(trie, sentence):
    sentence = sentence.lower().replace(',', ' ').replace('  ', ' ')
    res = []
    i=0
    while i < len(sentence):
        if i==0 or sentence[i-1] == ' ' or sentence[i-1] == '\n':
            longest_sentence = ''
            longest_sentence_j = 0
            for j in range(i+1, len(sentence)+1):
                if j == len(sentence) or sentence[j] == ' ' or sentence[j] == '\n':
                    sub_sentence = sentence[i:j]
                    # print(repr(sub_sentence))
                    # if sub_sentence == '.net core':
                    #     print('aloalo')
                    searched_value = trie.search(sub_sentence)
                    if type(searched_value) == str:
                        break
                    elif trie.search(sub_sentence) == True:
                        longest_sentence = sub_sentence
                        longest_sentence_j=j-1
            if longest_sentence != '':
                res.append(longest_sentence)
                i = longest_sentence_j
        i+=1
    return list(set(res))

cur_index = 4

df = pd.read_csv('extracted_ITjobs.csv')
df['job_detail_job_requirements'] = df['job_detail_job_requirements'].apply(ast.literal_eval)
df['job_detail_job_requirements_line'] = df['job_detail_job_requirements_line'].apply(ast.literal_eval)

f = open("skill_list.txt", "r")
skill_list = list(f)
trie_directory = '/trie_struture'
skill_list = [x.lower() for x in skill_list]

# for x in df['job_detail_job_requirements']:
#     skill_list.extend(x)

skill_list = list(set(skill_list))

file = open('skill_list.txt','w')
for skill in skill_list:
	file.write(skill.replace('\n', '').rstrip()+"\n")
file.close()

trie = Trie()
for skill in skill_list:
    trie.insert(skill)

tmp_string = '\n'.join(df.iloc[cur_index]['job_detail_job_requirements_line']).lower()
# tmp_string = """
# azure copilot.
# .net core.
# """
# tmp_string = "- Nẵm vững HTML,CSS,SCSS,JS"
tmp_string = tmp_string.replace('. ', ' ').replace('.\n', '\n').replace('/ ', ' ').replace('  ', ' ')
if tmp_string[-1] == '.':
    tmp_string = tmp_string[:-1]

searched_skill = search_in_trie(trie, tmp_string)
print(searched_skill)
searched_skill = search_in_trie(trie, tmp_string)

special_skill = [
    'r',
    'c'
]

for skill in searched_skill:
    pattern = re.escape(skill)
    tmp_string = re.sub(pattern, r'\033[32m\g<0>\033[0m', tmp_string)

print(tmp_string)

