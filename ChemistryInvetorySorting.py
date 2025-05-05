# Written by Qais Khadjazada
# Program is designed to assist chemists with exporting chemical structures and compounds they have created in a signals notebook to a CDD vault for inventory tracking. 
# Program intigrates Signals Notebook API with CDD vaults and creates hyperlinks for quick navigation.

import json
from re import sub as re_sub, escape as re_escape
from urllib.parse import unquote, quote
from requests import get, patch, post

debug = True # debugging output

def generateError(error,shouldLogToFile):
    print(error)
    exit()
def logMessage(msg,override):
    if(debug or override): 
        print(msg)


class sample:
    # sample of compound
    # all manipulation of sample data done & stored here
    

    """
    responsibleChemist = ""
    locationSynthesized = ""
    labNotebookPage = ""
    registrationDate = ""
    CRO-ID = ""
    initialAmount = ""
    purity = ""
    storageLocation = ""
    iupac = ""
    projectName = ""
    projectID = 0
    sampleID = ""
    salt = ""
    """
    error = ""      
    def __init__(self, sampleID):
        self.sampleID = sampleID
    def __findJsonID(self,objects,id):
        for ob in objects:
            if ob['id'] == str(id):
                return ob
        return False
    def __findSampleOwner(self,object):
        # included
        dataSet = self.__findJsonID(object,self.sampleID)
        userID = dataSet['relationships']['createdBy']['data']['id']
        userName = self.__findJsonID(object,str(userID))
        firstName = userName['attributes']['firstName']
        lastName = userName['attributes']['lastName']
        return (firstName + " " + lastName)






    def __isSampleValid(self):
        if len(self.error) > 0:
            generateError("Error within Sample Data!<br>" + self.error,True)
        else: 
            logMessage("sample is valid",False)
            return(True)
    def parseSampleResponse(self, response):
        data = response['data']
        included = response['included']
        #
        # responsible chemist
        try:
            self.responsibleChemist = self.__findSampleOwner(included)
        except:
            self.error += "&emsp;Responsible Chemist (?)<br>"
            pass
        else:
            logMessage("found chemist - " + self.responsibleChemist,False)
        #
        # notebook page
        try:
            self.labNotebookPage = self.__findJsonID(data,"b718adec-73e0-3ce3-ac72-0dd11a06a308")['attributes']['content']['value']
        except:
            self.error += "&emsp;Lab Notebook Page (?)<br>"
            pass
        else:
            logMessage("found notebook page - " + self.labNotebookPage,False)
        #
        # registration date
        try:
            self.registrationDate = self.__findJsonID(included,self.sampleID)['attributes']['createdAt'][:10]
        except:
            self.error += "&emsp;Registration Data (?)<br>"
            pass
        else:
            logMessage("found sample registration date - " + self.registrationDate,False)


        #Salt Name 
        #check to see if salt exists if so grab salt code 
        try:
            self.salt = self.__findJsonID(included,self.sampleID)['attributes']['fragments']['salts'][0]['name']
            self.salt = self.salt[self.salt.find("(")+1:self.salt.find(")")]
        except:
            #self.error += "&emsp;salts<br>"
            self.salt = "AA" #if no salt is found set the code for no salt
            logMessage("No Salt Found, Default value - " + self.salt,False)
            pass
        else:
            logMessage("found salt - " + self.salt,False)


        try:
            self.saltCoef = str(self.__findJsonID(included,self.sampleID)['attributes']['fragments']['salts'][0]['coefficient'])
        except:
            #self.error += "&emsp;salts<br>"
            self.saltCoef = "0" #if no salt is found set the code for no salt
            logMessage("Salt Coef has not been changed, Default value - " + self.saltCoef,False)
            pass
        else:
            logMessage("found salt Coefficient- " + self.saltCoef,False)






        try:
            self.croID = self.__findJsonID(data,117)['attributes']['content']['value']
        except:
            self.error += "&emsp;CRO-ID (?)<br>"
            pass
        else:
            logMessage("found sample CRO-ID - " + self.croID,False)





        # iupac name
        try:
            self.iupac = self.__findJsonID(data,116)['attributes']['content']['value']
        except:
            self.error += "&emsp;IUPAC Name<br>"
            pass
        else:
            logMessage("found IUPAC - " + self.iupac,False)
        #
        # location synthesized
        try:
            self.locationSynthesized = self.__findJsonID(data,106)['attributes']['content']['value']
        except:
            self.error += "&emsp;Location Synthesized<br>"
            pass
        else: 
            logMessage("found location synthesized - " + self.locationSynthesized,False)
        #
        # initial amount
        try:
            self.initialAmount = self.__findJsonID(data,4)['attributes']['content']['value']
            if type(self.initialAmount) != bool:
                if ' g' in self.initialAmount:
                    self.initialAmount = re_sub('\sg$', '', self.initialAmount)
                elif ' µg' in self.initialAmount:
                    self.initialAmount = re_sub('\sµg$', '', self.initialAmount)
                    self.initialAmount = str('%f' %(int(self.initialAmount)/1000000))
                elif ' mg' in self.initialAmount:
                    self.initialAmount = re_sub('\smg$', '', self.initialAmount)
                    self.initialAmount = str('%f' %(int(self.initialAmount)/1000))
                elif ' kg' in self.initialAmount:
                    self.initialAmount = re_sub('\skg$', '', self.initialAmount)
                    self.initialAmount = str('%f' %(int(self.initialAmount)*1000))
        except:
            self.error += "&emsp;Initial Amount<br>"
            pass
        else:
            logMessage("found initial amount - " + self.initialAmount,False)
        #       
        # purity
        try:
            self.purity = self.__findJsonID(data,109)['attributes']['content']['value']
        except:
            self.error += "&emsp;Purity<br>"
            pass
        else:
            logMessage("found purity % - " + self.purity,False)
        #
        # storage location
        try:
            self.storageLocation = self.__findJsonID(data,110)['attributes']['content']['value']
        except:
            self.error += "&emsp;Storage Location<br>"
            pass
        else:
            logMessage("found storage location - " + self.storageLocation,False)
        #   
        # project name
        try:
            self.projectName = self.__findJsonID(data,103)['attributes']['content']['value']
        except:
            self.error += "&emsp;Project Name (?)<br>"
            pass
        else:
            logMessage("found project name - " + self.projectName,False)
        #       
        # check for existing link
        temp = self.__findJsonID(data,111)
        try:
            link = temp['attributes']['content']['value']
            name = temp['attributes']['content']['name']
        except:
            logMessage("no link found on sample",False)
            pass
        else: 
            logMessage("found link on sample - " + name + " --> " + link,True)
            # don't break if we find a link yet - replaced by batch duplication checks
            self.error += "&emsp;A Link already exists on Sample! <br> &emsp;&emsp;" + name + " --> " + link + "<br>" 
        self.__isSampleValid()
    def generateSubmissionJson(self):
        jsonData = ({
        "molecule": {
            "synonyms": [self.iupac, self.croID],
            "iupac_name": self.iupac
        },
        "projects": [self.projectID, self.projectName],
        "salt_name": self.salt,
        "batch_fields": {
            "Responsible Chemist": self.responsibleChemist,
            "Location Synthesized": self.locationSynthesized,
            "Lab Notebook Page #": self.labNotebookPage,
            "Registration Date": self.registrationDate,
            "Initial Amount (g)": self.initialAmount,
            "purity (%)": self.purity,
            "Storage Location": self.storageLocation,
            "CRO identifier": self.croID,

        },
        "stoichiometry": {
                "salt_count": self.saltCoef
            }
        })
        logMessage("Generated Sample JSON File to POST: "+json.dumps(jsonData),True)
        return(json.dumps(jsonData))
    def getProjectName(self):
        logMessage("returned projectName " + self.projectName , False)
        return self.projectName
    def setProjectID(self,id):
        self.projectID = id
        logMessage("set project id " + self.projectName + " --> " + str(self.projectID),False)
    def getMoleculeName(self):
        return(self.iupac)
    def generateSearchDupeJson(self):
        jsonData = ({
            "fields_search": [
            {"name":"Storage Location", "text_value": self.storageLocation},
            {"name":"Responsible Chemist", "text_value": self.responsibleChemist},
            {"name":"Location Synthesized", "text_value": self.locationSynthesized},
            {"name":"Lab Notebook Page #", "text_value": self.labNotebookPage},
            {"name":"Registration Date", "date_value": self.registrationDate},
            {"name":"Initial Amount (g)", "float_value": self.initialAmount},
            {"name":"purity (%)", "float_value": self.purity},
            ],
            "async":"false"
        })
        logMessage("Generated Search For Dupe JSON File to GET: "+json.dumps(jsonData),True)
        return(json.dumps(jsonData))

class notebook:
    # signals notebook
    # all interactions with signals notebook done through here
    def __init__(self, baseUrl, apiKey):
        self.baseUrl = baseUrl
        self.apiKey = apiKey
    def getSampleData(self,sampleID):
        myURI = self.baseUrl + "samples/" + sampleID + "/properties"
        response = get(myURI,headers={'x-api-key': self.apiKey})
        if response.status_code != 200:
            generateError("Unable to get Sample Data - Signals Notebook<br>" + str(response.status_code) + "<br>" + response.text,True)
        logMessage("recieved sample data from signals notebook",False)
        return(json.loads(response.text))
    def patchSampleLink(self,linkData, sampleID):
        myURI = self.baseUrl + "samples/" + sampleID + "/properties/111?force=true&value=display"
        response = patch(myURI, headers={'x-api-key': self.apiKey, 'Content-Type': 'application/vnd.api+json'}, data=linkData)
        if response.status_code != 200:
            generateError("Unable to Patch Link into Sample - Signals Notebook<br>" + str(response.status_code) + "<br>" + response.text,True)
        logMessage("patched link into signals notebook: " + json.loads(linkData)['data']['attributes']['content']['value'],True)
        return True

class CDDVault:
    def __init__(self, baseUrl, apiKey, vaultID):
        self.apiKey = apiKey
        self.url = baseUrl + str(vaultID) + "/"
    def getProjectID(self, projectName):
        myURI = self.url + "projects"
        response = get(myURI, headers={'X-CDD-Token': self.apiKey})
        logMessage("recieved response to getProjectID " + str(response.status_code) + " " + response.text,False)
        if response.status_code != 200:
            generateError("Unable to Get Project ID - CDD Vault<br>" + str(response.status_code) + "<br>" + response.text,True)
        for projects in json.loads(response.text):
            if projects['name'] == projectName:
                logMessage("matched project id: " + str(projects['id']) + " - " + projectName,False)
                return projects['id']
        generateError("Unable to find matching Project in CDD Vault",True)
    def postBatch(self,jsonSample):
        myURI = self.url + "batches"
        response = post(myURI, headers={'X-CDD-Token': self.apiKey, 'Content-Type': 'application/json'}, data=jsonSample)
        if response.status_code != 200:
            generateError("Unable to Post Sample Batch - CDD Vault<br>" + str(response.status_code) + "<br>" + response.text,True)
        response = json.loads(response.text)
        myMoleculeID = str(response['molecule']['id'])
        myMoleculeName = response['molecule_batch_identifier']
        myMoleculeLink = self.url + "molecules/" + myMoleculeID + "#molecule-batches"
        myMoleculeLink = re_sub("api/v1/", "", myMoleculeLink)
        logMessage("posted batch to cdd vault: " + myMoleculeName + " -- " + myMoleculeLink,False)
        myResponse = json.dumps({
            "data": {
                "attributes": {
                    "content": {
                        "name": myMoleculeName,
                        "value": myMoleculeLink
                    }
                }
            }
        })
        return myResponse
    def getDupeBatch(self, dupeCheckJson,cddMoleculeID):
        myURI = self.url + "batches"
        response = get(myURI, headers={'X-CDD-Token': self.apiKey, 'Content-Type': 'application/json' }, data=dupeCheckJson)
        #logMessage("recieved response to getDupeBatches " + str(response.status_code) + " " + response.text,False)
        if response.status_code != 200:
            generateError("Unable to Get Dupe Batches - CDD Vault<br>" + str(response.status_code) + "<br>" + response.text,True)
        dupeResponse = json.loads(response.text)
        if dupeResponse['count'] > 0:
            for batch in dupeResponse['objects']:
                if batch['molecule']['id'] == cddMoleculeID:
                    cddVaultLink = self.url+ "molecules/" + str(cddMoleculeID) + "#molecule-batches"
                    cddVaultLink = re_sub("api/v1/","",cddVaultLink)
                    generateError("This Batch has been submitted to CDD Vault previously: <a href=\"" + cddVaultLink + "\">" + batch['name'] + "</a>",True)
        return(False)
    def getMoleculeID(self,name):
        myURI = self.url + "molecules?page_size=1000&no_structures=true"
        #URIname = "'" + name + "'"
        #myURI = myURI + "?names=" + quote(URIname)
        #logMessage(myURI,True)
        response = get(myURI, headers={'X-CDD-Token': self.apiKey})
        if response.status_code != 200:
            generateError("Unable to Get Molecule ID - CDD Vault<br>" + str(response.status_code) + "<br>" + response.text,True)
        response = json.loads(response.text)
        if response['count'] > 1:
            #logMessage("There appears to be more than one molecule with that IUPAC",True)
            for molecule in response['objects']:
                for names in molecule['synonyms']:
                    if names == name:
                        logMessage("Found matching Molecule: " + str(molecule['id']),False)
                        return molecule['id']
        elif response['count'] == 0:
            generateError("There are no Molecules",True)
        #logMessage("test - " + name + " -- " + str(response['objects']),True)
        return(False)

# signals notebook (account registered must have access to notebooks)
signalsApiKey = ''
signalsBaseUrl = ''

# cdd vault (account must have access to projects being registered within)
cddApiKey = ''
cddBaseUrl = ''
cddVaultID = 5821
#cddVaultID = 5974

# our test data (replace with data recieved from POST)
#sampleID = "sample:afab8d10-0d4f-4ef2-aa6a-40563812eea9"
sampleID = ''

# the following try/catch block catches any errors we find, logs & a response are generated

myNotebook = notebook(signalsBaseUrl, signalsApiKey) # initilize our signals notebook api connection
myVault = CDDVault(cddBaseUrl, cddApiKey, cddVaultID) # initialize our vault api connection
mySample = sample(sampleID) # create our sample object

sampleData = myNotebook.getSampleData(sampleID) # get sample data from notebook
mySample.parseSampleResponse(sampleData) # add sample data to sample object




print(mySample)


projectName = mySample.getProjectName()
projectID = myVault.getProjectID(projectName) # get project id that matches our project name

mySample.setProjectID(projectID) # set project id in our sample

sendToCDD = mySample.generateSubmissionJson() # generate our cdd vault json


moleculeName = mySample.getMoleculeName() # get iupac name
cddMoleculeID = myVault.getMoleculeID(moleculeName) # find molecule_id from cdd vault
if (cddMoleculeID):
    myVault.getDupeBatch(mySample.generateSearchDupeJson(),cddMoleculeID) # check for duplicate batches of our molecule and break if needed

print(sendToCDD)
patchData = myVault.postBatch(sendToCDD) # post our data to cdd vault
myNotebook.patchSampleLink(patchData,sampleID) # write our link back to signals notebook

exit()
