#!/usr/bin/env python3
# -------------------------------------------
# Passcast, a custom password list generator.
# Author: Scragg
# Date: 09/10/2022
# -------------------------------------------

# Import
import argparse
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
                data = open(input("Wordlist path and filename:"), 'r').read().split('\n')
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
                            "\t3) This is more of an art than a science, put yourself in the users shoes.\n")
    for q in questions:
        for w in askQuestion(q).split(','):
            data.append(w.strip())
    printGreen("\nGenerating words...")
    words = generateSeeds(data)
    printGreen("Done.")
    mangle = input("\nContinue to mangler [y/n]?")
    if mangle.lower() != 'y':
        mangle = input("\nAre you sure you don't want to use the mangler [y/n]?")
        if mangle.lower() == 'n':
            mangle(words)
        else:
            saveList(input("\nOutput path and filename (appends if the file already exists):"), words)
            print("Good luck :D")
    else:
        mangle(words)
    return

def generateSeeds(data):
    # Generate basic seeds from base words.
    res = []
    for d in data:
        if(len(d) == 10 and '-' in d):
            try:
                res.append(datetime.strptime(d, "%d-%m-%Y"))
            except:
                res.append(d)
        else:
            res.append(d)
    return res

def saveList(filename, words):
    done = False
    while not done:
        try:
            out = open(filename, "a")
            for w in words:
                if isinstance(w, datetime):
                    out.write(str(w.date()+"\n"))
                else: 
                    out.write(w+"\n")
            done = True
        except:
            printRed("Unable to save list to: "+filename)
            filename = input("\nOutput path and filename (appends if the file already exists):")
    print("Wordlist saved.")

def mangle(words):
    # Advanced password generation from seed words.
    print("Time for the real stuff...")
    saveList(input("\nOutput path and filename (appends if the file already exists):"), words)
    print("Good luck :D")

def printBanner():
    # Clear Screen
    print("\033[2J\033[H")
    # Print Banner
    printGreen("\n██████╗  █████╗ ███████╗███████╗ ██████╗ █████╗ ███████╗████████╗\n██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝╚══██╔══╝\n██████╔╝███████║███████╗███████╗██║     ███████║███████╗   ██║   \n██╔═══╝ ██╔══██║╚════██║╚════██║██║     ██╔══██║╚════██║   ██║   \n██║     ██║  ██║███████║███████║╚██████╗██║  ██║███████║   ██║   \n╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   \n")
    printRed("=================================================================")
    return

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