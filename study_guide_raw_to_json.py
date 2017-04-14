import PyPDF2
import json

questions = []

with open('study_guide_2_raw.txt', 'r') as f:
  content = f.readlines()

content = [x.strip() for x in content]

length = len(content)

x = 0

while x < length:
  current = {}

  question = ''
  while x < length and content[x] != 'A.':
    question = question + content[x]
    x += 1

  current['question'] = question
  last = None

  if x+1 < length and content[x] == 'A.':
    current['A'] = content[x+1]
    x += 2
    last = 'A'

  if x+1 < length and content[x] == 'B.':
    current['B'] = content[x+1]
    x += 2
    last = 'B'

  if x+1 < length and content[x] == 'C.':
    current['C'] = content[x+1]
    x += 2
    last = 'C'

  if x+1 < length and content[x] == 'D.':
    current['D'] = content[x+1]
    x += 2
    last = 'D'

  if x+1 < length and content[x] == 'E.':
    current['E'] = content[x+1]
    x += 2
    last = 'E'

  if last is not None:
    current['answer'] = current[last][-1:]
    current[last] = current[last][:-2]
    current['status'] = 'ok'
    if current['answer'] not in 'ABCDE':
      current['status'] = 'error'
  else:
    current['status'] = 'error'
    
  questions.append(current)

#print(json.dumps(questions))

error = [x for x in questions if x['status'] is 'error']
good = [x for x in questions if x not in error]

print(json.dumps(good))
