class Extractedfiles:
    def __init__(self):
        self.files = []
    
    def readData(self):
        for i in range(56):
            filename = f'Trump Speechs/Trump Speechs/Speech_{i}.txt'
            lines= []
            with open(filename) as file:
                lines = file.readlines()
            
            temp =''
            for line in lines:
                if line == "\n":
                    continue
                
                if "\n" in line:
                    temp += line.replace("\n", ".")
                else:
                    temp += line
                    
                self.files.append(temp)
    
    
    def getfiles(self):
        return self.files





# with open('Trump Speechs\Trump Speechs\Speech_' + str(0) + '.txt') as file:
#     print(file.readlines())
    