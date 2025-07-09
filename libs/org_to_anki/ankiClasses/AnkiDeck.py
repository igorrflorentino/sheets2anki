from .AnkiQuestion import AnkiQuestion
# from .AnkiQuestionMedia import AnkiQuestionMedia

class AnkiDeck:

    # Basic file => represented in a single deck
    # MultiDeck file => File will have multiple subdecks of general topic
    # represented by file
    def __init__(self, name): # (str)
        self.deckName = name
        self.subDecks = []
        self._ankiQuestions = []
        self._parameters = {}
        self._comments = []
        self._media = []
        self._sourceFilePath = ""

    def getMedia(self):
        media = []

        if self.hasSubDeck():
            for subDeck in self.subDecks:
                media.extend(subDeck.getMedia())
        media.extend(self._media)

        return media

    def addComment(self, comment): # (str)
        self._comments.append(comment)

    def getComments(self):
        return self._comments

    def addParameter(self, key, value): # (str, str)
        self._parameters[key] = value
    
    def getParameters(self):
        return dict(self._parameters)

    def getParameter(self, key, default=None):
        return self._parameters.get(key, default)

    def getQuestions(self, parentName = None, parentParamaters = None, joiner = '::'): # (str, dict, str)
        ankiQuestions = []

        for question in self._ankiQuestions:
            if parentName is not None:
                question.setDeckName(parentName + joiner + self.deckName)
            else:
                question.setDeckName(self.deckName)

            if parentParamaters is not None:
                for key in parentParamaters:
                    if self.getParameter(key) is None:
                        self.addParameter(key, parentParamaters[key])

            for key in self._parameters:
                if question.getParameter(key) is None:
                    question.addParameter(key, self._parameters[key])

            ankiQuestions.append(question)

        if self.hasSubDeck():
            name = self.deckName
            if parentName is not None:
                name = parentName + joiner + self.deckName
            if parentParamaters is not None:
                for key in parentParamaters:
                    if self.getParameter(key) is None:
                        self.addParameter(key, parentParamaters[key])

            for i in self.subDecks:
                ankiQuestions.extend(i.getQuestions(name, self._parameters))

        return ankiQuestions

    def getDeckNames(self, parentName = None, joiner = '::'): # (str, str)
        deckNames = []
        if parentName is not None:
            deckNames.append(parentName + joiner + self.deckName)
        else:
            deckNames.append(self.deckName)

        if self.hasSubDeck():
            name = self.deckName
            if parentName is not None:
                name = parentName + joiner + self.deckName
            for i in self.subDecks:
                deckNames.extend(i.getDeckNames(name))

        return deckNames

    def addQuestion(self, ankiQuestion): # (AnkiQuestion)
        # Add media to the main deck
        # TODO if question is removed its media will remain in the deck
        if ankiQuestion.hasMedia():
            self._media.extend(ankiQuestion.getMedia())
        self._ankiQuestions.append(ankiQuestion)

    def addSubdeck(self, ankiDeck):  # TODO Should have type of AnkiDeck
        self.subDecks.append(ankiDeck)

    def hasSubDeck(self):
        return len(self.subDecks) > 0

    def __str__(self):
        return ("DeckName: %s.\nSubDecks: %s.\nQuestions: %s.\nParamters: %s.\nComments: %s.\nMedia: %s") % (
            self.deckName, self.subDecks, self._ankiQuestions, self._parameters, self._comments, self._media)

    def __eq__(self, other):
        if other == None:
            return False
        return self.deckName == other.deckName and self.getDeckNames() == other.getDeckNames() and self.getQuestions() == other.getQuestions(
        ) and self.subDecks == other.subDecks and self._parameters == other._parameters and self._comments == other._comments and self._media == other._media
