#!/usr/bin/env python3
# -------------------------------------------
# Passcast, a custom password list generator.
# Author: Scragg
# Date: 09/10/2022
# -------------------------------------------

# Import
import argparse
from random import randint
from datetime import datetime

# Arguments
parser = argparse.ArgumentParser("passcast", description="Generate custom password lists. It just works.", add_help=False)
parser.add_argument("-h", "--help", action='help', help="Show this help message.")
parser.add_argument("-i", "--interactive", action='store_true', help="Start Passcast in interactive mode.")
parser.add_argument("-m", "--mangler", action='store_true', help="Start Passcast in mangler mode.")
args = parser.parse_args()

# Main function
def main():
    # Global variables
    global args

    # Validate Args
    if(args.interactive and args.mangler):
        print("Invalid flag commbination: -i and -m")
        return
    elif(not args.interactive and not args.mangler):
        print("Invalid argument set, use -h for help.")
        return

    # Welcome
    printBanner()
    
    # Handle Arguments
    if(args.interactive):
        interactive()
    elif(args.mangler):
        success = False
        while not success:
            try:
                data = open(input("Wordlist path and filename: "), 'r').read().split('\n')
                success = True
                mangle(data)
            except:
                printRed("Unable to find specified wordlist...")
    return

def interactive():
    # Store answer data
    data = []
    # Split questioning depending on target type
    mode = input("\nIs the target a company or person [c/p]? ")
    while mode.upper() != "C" and mode.upper() != "P":
        print("Invalid input. Enter C or P.")
        mode = input("Is the target a company or person [c/p]? ")
    questions = []
    if mode.upper()  == 'C':
        # Ask corporate questions
        questions = ["Company name [full & abbreviated]",
                    "Products and services",
                    "Significant employees",
                    "Slogans and mottos",
                    "Locations",
                    "Domains",
                    "Social media handles",
                    "Important dates [dd-mm-yyyy]",
                    "Where is this password used",
                    "Extra keywords"]
        printRed("Tips: \n\t1) You can add multiple answers for each question - separate answers with commas. (Example: cats,dogs,wifi,letmein)\n"+
                            "\t2) Break up words at natural breaks. (Example: Blackboard -> black,board,blackboard)\n"+
                            "\t3) This is more of an art than a science, put yourself in the admins shoes.\n"+
                            "\t4) Skip questions if you don't have that information.\n")
    elif mode.upper()  == 'P':
        # Ask personal questions
        questions = ["Name(s)",
                    "Occupation",
                    "Phone number",
                    "Address",
                    "Email",
                    "Friends and Family members",
                    "Pets",
                    "Holiday destinations",
                    "Sports teams",
                    "Social media handles",
                    "Important locations",
                    "Important dates [dd-mm-yyyy]",
                    "Personal identification information (e.g. SSN, Employee number...)"
                    "Where is this password used",
                    "Extra keywords"]
        printRed("Tips: \n\t1) You can add multiple answers for each question - separate answers with commas. (Example: cats,dogs,wifi,letmein)\n"+
                            "\t2) Break up words at natural breaks. (Example: Blackboard -> black,board,blackboard)\n"+
                            "\t3) This is more of an art than a science, put yourself in the users shoes.\n"+
                            "\t4) Skip questions if you don't have that information.\n")
    # Gather question answers from user
    for q in questions:
        for w in askQuestion(q).split(','):
            data.append(w.strip())
    printGreen("\nGenerating words...")
    words = generateSeeds(data)
    printGreen("Done.")
    mangle = input("\nContinue to mangler [y/n]? ")
    if mangle.lower() != 'y':
        mangle = input("\nAre you sure you don't want to use the mangler [y/n]? ")
        if mangle.lower() == 'n':
            mangle(words)
        else:
            saveList(input("\nOutput path and filename (appends if the file already exists): "), words)
            print("Good luck :D")
    else:
        mangle(words)
    return

# Generate basic seeds from base words.
def generateSeeds(data):
    # Word lists
    seeds = []
    tmp = []
    words = []

    # Break up dates into integers
    for d in data:
        if(len(d) == 10 and '-' in d):
            try:
                words.append(datetime.strptime(d, "%d-%m-%Y"))
            except:
                words.append(d)
        else:
            words.append(d)

    # Add originals to seeds
    for w in words:
        if not isinstance(w, datetime):
            tmp.append(w)
        else:
            tmp.append(str(w.date()))
            tmp.append(str(w.date().day))
            tmp.append(str(w.date().month))
            tmp.append(str(w.date().year))
    for t in tmp:
        seeds.append(str(t))
    tmp = []

    # All capitalisation variations
    opt = input("\nVary capitalization (approx."+str(len(seeds)*3)+" words) [Y/N]: ")
    while opt.upper() != 'Y' and opt.upper() != 'N':
        printRed("Illegal choice!")
        opt = input("Vary capitalization (approx."+str(len(seeds)*3)+" words) [Y/N]: ")
    if (opt.upper() == 'Y'):
        seeds = capitalVariation(seeds)

    # All combos with and without joining chars
    opt = input("\nCombine seed words with each other and with joining chars (approx. "+str(len(seeds)*len(seeds)*16)+" words) [Y/N]: ")
    while opt.upper() != 'Y' and opt.upper() != 'N':
        printRed("Illegal choice!")
        opt = input("Combine seed words with each other and with joining chars (approx. "+str(len(seeds)*len(seeds)*16)+" words) [Y/N]: ")
    if (opt.upper() == 'Y'):
        seeds = combine(seeds, [])

    # Append years
    opt = input("\nAppend years (current and the last 4) to the end of each word (approx. "+str(len(seeds)*5)+" words) [Y/N]: ")
    while opt.upper() != 'Y' and opt.upper() != 'N':
        printRed("Illegal choice!")
        opt = input("Append years (current and the last 4) to the end of each word (approx. "+str(len(seeds)*5)+" words) [Y/N]: ")
    if (opt.upper() == 'Y'):
        seeds = appendYears(seeds, [])

    # Leet chars
    opt = input("\nSubstitute some chars like a hacker e.g. L33t 3nc0d1ng (approx. "+str(len(seeds)*3)+" words) [Y/N]: ")
    while opt.upper() != 'Y' and opt.upper() != 'N':
        printRed("Illegal choice!")
        opt = input("Substitute some chars like a hacker e.g. L33t 3nc0d1ng (approx. "+str(len(seeds)*3)+" words) [Y/N]: ")
    if (opt.upper() == 'Y'):
        seeds = leetSubs(seeds)

    # Remove duplicates
    printRed("Removing duplicates...")
    seeds = list(dict.fromkeys(seeds))

    # Output Stats
    print("Word count:", len(seeds))
    return seeds

# Make l33t character substitutions
def leetSubs(seeds):
    tmp = []
    for w in seeds:
        if randint(0, 2) < 2 and 'a' in w.lower():
            tmp.append(w.replace('a', '@').replace('A', '@'))
        if randint(0, 2) < 2 and 'e' in w.lower():
            tmp.append(w.replace('e', '3').replace('E', '3'))
        if randint(0, 2) < 2 and 'o' in w.lower():
            tmp.append(w.replace('o', '0').replace('O', '0'))
        if randint(0, 2) < 2 and ('e' in w.lower() or 'o' in w.lower()):
            tmp.append(w.replace('o', '0').replace('O', '0').replace('e', '3').replace('E', '3'))
        if randint(0, 2) < 2 and ('a' in w.lower() or 'e' in w.lower()):
            tmp.append(w.replace('a', '@').replace('A', '@').replace('e', '3').replace('E', '3'))
        if randint(0, 2) < 2 and ('a' in w.lower() or 'o' in w.lower()):
            tmp.append(w.replace('a', '@').replace('A', '@').replace('o', '0').replace('O', '0'))
    for t in tmp:
        seeds.append(t)
    return seeds

# Vary capitalisation: Natural, all caps, all lower.
def capitalVariation(seeds):
    tmp = []
    for w in seeds:
        if not isinstance(w, datetime):
            up = w.upper()
            lo = w.lower()
            std = w.capitalize()
            if w != lo:
                tmp.append(lo)
            if w != up:
                tmp.append(up)
            if w != std:
                tmp.append(std)
    for t in tmp:
        seeds.append(str(t))
    return seeds

# Combine all words together with joiners and withour joiners.
def combine(seeds, joiners):
    tmp = []
    if joiners == []:
        joiners = ['', '@', '_', '-', ',', '#', '&', '>', '<', '|', '\\', '/', ':', '+', '=', ' ']
    for a in seeds:
        for b in seeds:
            for c in joiners:
                if a != b:
                    tmp.append(str(a)+c+str(b))
    for t in tmp:
        seeds.append(str(t))
    return seeds

# Append current and last 4 years on the end of each word.
def appendYears(seeds, joiners):
    tmp = []
    curr_year = int(datetime.today().year)
    years = [str(curr_year), str(curr_year-1), str(curr_year-2), str(curr_year-3), str(curr_year-4)]
    if joiners == []:
        joiners = ['', '@', '_', '+', '=', '#', '!', '&', '-']
    for w in seeds:
        for y in years:
            for j in joiners:
                tmp.append(str(w)+j+str(y))
    for t in tmp:
        seeds.append(str(t))
    return seeds

# Save the wordlist to a file
def saveList(filename, words):
    done = False
    while not done:
        try:
            out = open(filename, "a")
            for w in words:
                if isinstance(w, datetime):
                    out.write(str(w.date()+"\n"))
                else: 
                    out.write(str(w)+"\n")
            done = True
        except:
            printRed("Unable to save list to: "+filename)
            filename = input("\nOutput path and filename (appends if the file already exists): ")
    print("Wordlist saved.")

# Advanced password generation from seed words.
def mangle(words):
    
    print("Time for the real stuff...")
    saveList(input("\nOutput path and filename (appends if the file already exists): "), words)
    print("Good luck :D")

# Print welcome text
def printBanner():
    # Clear Screen
    print("\033[2J\033[H")
    # Print Banner
    printGreen("\n?????????????????????  ?????????????????? ???????????????????????????????????????????????? ????????????????????? ?????????????????? ???????????????????????????????????????????????????\n???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????\n?????????????????????????????????????????????????????????????????????????????????????????????????????????     ????????????????????????????????????????????????   ?????????   \n????????????????????? ?????????????????????????????????????????????????????????????????????????????????     ????????????????????????????????????????????????   ?????????   \n?????????     ?????????  ??????????????????????????????????????????????????????????????????????????????????????????  ?????????????????????????????????   ?????????   \n?????????     ?????????  ????????????????????????????????????????????????????????? ??????????????????????????????  ?????????????????????????????????   ?????????   \n")
    printRed("=================================================================")
    return

# Printing coloured text
def printGreen(data):
    print("\u001b[32m"+data+"\u001b[37m")
    return

def printRed(data):
    print("\u001b[31m"+data+"\u001b[37m")
    return

def askQuestion(data):
    print("\u001b[36m"+data+": \u001b[37m", end="")
    ans = input("")
    return ans

# Execute main on start up
if __name__ == "__main__":
    main()