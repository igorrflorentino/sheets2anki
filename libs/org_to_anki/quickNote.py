from . import utils
from . import config

def quickNote():
    utils.createQuickNotesFile()

    question = input("Enter the question.\n").strip()
    newQuestion = "* " + question + "\n"

    while True:
        answer = input(
            "Enter an answer. Enter blank answer to exit.\n").strip()
        if answer == "":
            break
        else:
            newQuestion += "** " + answer + "\n"

    writeQuickNote(newQuestion)


def writeQuickNote(question, filePath=None):
    if filePath is None:
        filePath = config.quickNotesOrgPath
    with open(filePath, "a") as orgFile:
        orgFile.write(question)


if __name__ == "__main__":
    quickNote()
