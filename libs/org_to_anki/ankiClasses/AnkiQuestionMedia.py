class AnkiQuestionMedia:

    def __init__(self, mediaType, fileName, data, imageUrl=None, imageFunction=None):
        self.mediaType = mediaType
        self.fileName = fileName
        self.data = data
        self.imageUrl = imageUrl
        self.imageFunction = imageFunction

        # Allow images to be lazy loaded
        if self.data == None and self.imageUrl != None and self.imageFunction != None:
            self.lazyLoad = True
        else:
            self.lazyLoad = False
    
    def lazyLoadImage(self):
        self.data = self.imageFunction(self.imageUrl)
        self.lazyLoad = False

    def __str__(self):
        return ("Media data for file type: %s and name %s") % (self.mediaType, self.fileName)
    
    def __eq__(self, other):
        return self.mediaType == other.mediaType and self.fileName == other.fileName and self.data == other.data

