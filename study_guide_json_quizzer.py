#!/usr/bin/python3

import random
import json
import sys
import os

#TODO: keep track of which specific questions you get wrong
#TODO: write results to a file to load in specific versions
#TODO: simple statistics like total questions answered, attempts, score, etc.

#keep track of current questions, correct, and incorrect
questions = []
correct = []
incorrect = []
bank = []

#colors for printing to the console
class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

#the parameters that can be set
class settings:
  JSON_FILE = None
  SAVE_OUT = None
  LOAD_IN = None

#main program
def run():
  global questions, correct, incorrect, bank
  
  #read in commands
  parse_args()

  #if we are loading in a past session
  if settings.LOAD_IN is not None:
    load()
  #otherwise open the json file and capture every line
  else:
    #was there not a parameter?
    if settings.JSON_FILE is None:
      print("Please specify path to JSON file")
      settings.JSON_FILE = input(" > ")
    
    try:
      with open(settings.JSON_FILE, 'r') as file:
        content = file.readlines()
    except:
      print("Could not find the input file \"" + settings.JSON_FILE + "\".")
      sys.exit(1)
      
    #strip off new line characters and merge lines into one string
    content = [x.strip() for x in content]
    content = ''.join(content)

    #convert json object into list
    bank = json.loads(content)
  
  #process every question
  while len(bank) > 0 or len(questions) > 0 or len(incorrect) > 0:
    #if we've answered all of the questions, then grab some more
    if len(questions) == 0 and len(incorrect) == 0:
      #print the nice message only if we've already been here
      if len(correct) > 0:
        print(bcolors.HEADER + "Questions completed!" + bcolors.ENDC)
        print(bcolors.HEADER + "Selecting another " + str(min(8,len(bank)) + min(2,len(correct))) + "!" + bcolors.ENDC)
      #pull random from bank (unseen)
      unseen = random.sample(bank, min(8, len(bank)))
      #pull random from correct (seen)
      seen = random.sample(correct, min(2, len(correct)))
      questions.extend(unseen)
      questions.extend(seen)
      for q in unseen:
        bank.remove(q)
      for q in seen:
        correct.remove(q)
      random.shuffle(questions)

    #if we've run out of questions, add all
    #incorrect questions back in the pool
    elif len(questions) == 0:
      print(bcolors.HEADER + "You got", len(incorrect), "wrong!" + bcolors.ENDC)
      print(bcolors.HEADER + "Adding those questions back into the pool!" + bcolors.ENDC)
      questions.extend(incorrect)
      #reset incorrect again
      incorrect = []

    #pick a random question
    current = random.randint(0, len(questions)-1)
    question = questions.pop(current)

    #call the method to ask this question
    is_correct, answer = ask_question(question)

    #question is not valid
    if is_correct is None:
      pass
    #answer was correct
    elif is_correct:
      print(bcolors.BOLD + bcolors.OKGREEN + "CORRECT" + bcolors.ENDC)
      correct.append(question)
    #answer was not correct
    else:
      print(bcolors.BOLD + bcolors.FAIL + "INCORRECT" + bcolors.ENDC)
      print("The answer was", answer)
      incorrect.append(question)

#method saves the current stats
def save():
  global questions, correct, incorrect, bank
  
  version = 1
  #if no save file was specified, then ask for one.
  if settings.SAVE_OUT is None:
    print("Please specify path to output file")
    settings.SAVE_OUT = input(" > ")
  #try to open the file and save the stats
  try:
    output = {"bank":bank, "questions":questions, "correct":correct, "incorrect":incorrect,
              "version": version}
    with open(settings.SAVE_OUT, "w") as f:
      f.write(json.dumps(output))
    print("Saved.")
  #could not open this file for some reason.
  except:
    print("Could not open the output file \"" + settings.SAVE_OUT + "\".")
    print("Save failed.")

#method loads previous stats            
def load():
  global questions, correct, incorrect, bank
  
  #this wouldn't make sense, but..
  if settings.LOAD_IN is None:
    print("No input file was provided.")
    sys.exit(1)
  
  try:
    with open(settings.LOAD_IN, "r") as f:
      content = f.readlines()
  except:
    print("Could not open the load file \"" + settings.LOAD_IN + "\".")
    print("Load failed.")
    sys.exit(1)

  #strip off new line characters and merge lines into one string
  content = [x.strip() for x in content]
  content = ''.join(content)

  #convert json object into list
  data = json.loads(content)
  
  #grab the version
  version = data["version"]
    
  #depending on the version, load in the data!
  if version == 1:
    questions = data["questions"]
    correct = data["correct"]
    incorrect = data["incorrect"]
    bank = data["bank"]
  
#method that sets the settings class variables
def parse_args():
  a = 1
  while a < len(sys.argv):
    arg = sys.argv[a]
    #help argument
    if arg in ['-h','--help']:
      print_help()
      sys.exit(0)
      return
    #input file argument
    elif arg in ['-i','--input-file']:
      try:
        settings.JSON_FILE = sys.argv[a+1]
        a += 1
      except:
        print("Missing argument after \"" + arg + "\"")
        print_help()
        sys.exit(1)
    #save output file argument
    elif arg in ['-o','--output-file']:
      try:
        settings.SAVE_OUT = sys.argv[a+1]
        a += 1
      except:
        print("Missing argument after \"" + arg + "\"")
        print_help()
        sys.exit(1)
    #load in file argument
    elif arg in ['-l','--load']:
      try:
        settings.LOAD_IN = sys.argv[a+1]
        a += 1
      except:
        print("Missing argument after \"" + arg + "\"")
        print_help()
        sys.exit(1)
    #unknown argument
    else:
      print("Unknown argument \"" + arg + "\"")
      print_help()
      sys.exit(1)

    a += 1
    
#method to display the help file
def print_help():
  help = "Usage: " + sys.argv[0] + " [OPTION...]" + \
  """
  
  -i, --input-file    specify which JSON file to load questions from
  -o, --output-file   specify which output file to save progress
  -l, --load          load and continue previously saved progress
  -h, --help          give this help list"""
  
  print(help)

#method displays
def ask_question(question):
  global questions, correct, incorrect, bank
  keys = question.keys()
  non_options = ['answer','question','status']
  options = [k for k in keys if k not in non_options]
  options.sort()
  
  #if this is a valid question
  if 'question' in keys and \
     'answer' in keys and \
     'status' in keys and \
     question['status'] == 'ok':

    #print the question
    print('\n\n' + bcolors.BOLD + bcolors.WARNING
     + question['question'] + bcolors.ENDC)

    #print the options
    for o in options:
      print(o + ')', question[o])
    
    #capture valid user input
    user = ' '
    while len(user) > 1 or user is '' or user not in options:
      user = input(' > ').upper()
      #check for quit
      if user == 'Q':
        print('Are you sure you want to quit?')
        #user must say 'yes' or 'no'
        while user not in ['yes','no']:
          user = input(' > ').lower()
        #they said yes to quit
        if user == 'yes':
          #if there is a output file, then save.
          if settings.SAVE_OUT is not None:
            save()
          #if there is not, then ask if they want to save.
          else:
            user = ""
            print("Would you like to save?")
            #user must say 'yes' or 'no'
            while user not in ['yes','no']:
              user = input(' > ').lower()
            if user == 'yes':
              save()
          #regardless if it was saved, they said yes to quit, so exit.
          sys.exit(0)
        #they said no to quit, remind the question and options for them.
        else:
          #print the question
          print('\n\n' + bcolors.BOLD + bcolors.WARNING
           + question['question'] + bcolors.ENDC)

          #print the options
          for o in options:
            print(o + ')', question[o])

    #get and compare the correct answer
    answer = question['answer']
    if user == answer:
      return (True, answer + ": " + question[answer])
    else:
      return (False, answer + ": " + question[answer])

  #the question is not valid, return None instead
  else:
    return None

if __name__ == '__main__':
  run()
