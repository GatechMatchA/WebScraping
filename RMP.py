import requests
import json
import math
from datetime import datetime

# Review
# {
#     "professorFName"
#     "professorLName"
#     "courseCode": "rClass"
#     "upVote": "helpCount"
#     "downVote": "notHelpCount"
#     "comment": "rComments"
#     "timeStamp":"rTimestamp"
#     "tags": "teacherRatingTags"
#     "easiness": "rEasy"
#     "quality":"rOverall"
# }


class RateMyProfScraper:
    def __init__(self, schoolid):
        self.UniversityId = schoolid
        self.professorlist = self.createprofessorlist()
        self.indexnumber = False

    # creates List object that include basic information on all Professors from the IDed University
    def createprofessorlist(self):
        pofessor_list = []
        num_of_prof = self.GetNumOfProfessors(self.UniversityId)
        num_of_pages = math.ceil(num_of_prof / 20)
        i = 1
        while (i <= num_of_pages):  # the loop insert all professor into list
            page = requests.get("http://www.ratemyprofessors.com/filter/professor/?&page=" + str(
                i) + "&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" + str(
                self.UniversityId))
            temp_jsonpage = json.loads(page.content)
            temp_list = temp_jsonpage['professors']
            pofessor_list.extend(temp_list)
            i += 1
        return pofessor_list

    # function returns the number of professors in the university of the given ID.
    def GetNumOfProfessors(self, id):
        page = requests.get(
            "http://www.ratemyprofessors.com/filter/professor/?&page=1&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" + str(
                id))  # get request for page
        temp_jsonpage = json.loads(page.content)
        num_of_prof = temp_jsonpage[
            'remaining'] + 20  # get total number of professors
        return num_of_prof

    def GetProfessorDetail(self):
        reviews_list = []
        for professor in self.professorlist:
            professorId = professor['tid']
            professorFirstName = professor['tFname']
            professorLastName = professor['tLname']
            num_of_reviews = self.GetNumOfReviews(professorId)
            num_of_pages = math.ceil(num_of_reviews / 20)
            # ratings_list = [[professorFirstName, professorLastName]]
            i = 1
            while (i <= num_of_pages):  # the loop insert all details into list
                page = requests.get("https://www.ratemyprofessors.com/paginate/professors/ratings?tid=" +
                                    str(professorId) + "&filter=&courseCode=&page=")
                temp_jsonpage = json.loads(page.content)
                temp_list = temp_jsonpage['ratings']
                for rating in temp_list:
                    time = int(str(rating["rTimestamp"])[0:9])
                    json_data = {
                        "professorFName": professor['tFname'],
                        "professorLName": professor['tLname'],
                        "courseCode": rating["rClass"],
                        "upVote": rating["helpCount"],
                        "downVote": rating["notHelpCount"],
                        "comment": rating["rComments"],
                        "timeStamp": datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'),
                        "tags": rating["teacherRatingTags"],
                        "easiness": rating["rEasy"],
                        "quality": rating["rOverall"]
                    }
                    reviews_list.append(json_data)
                i += 1
        # print(reviews_list[0])
        reviews_json = {"reviews": reviews_list}
        with open('reviews.json', 'w') as fout:
            json.dump(reviews_json, fout)
        return reviews_json

    def GetNumOfReviews(self, professorId):
        page = requests.get(
            "https://www.ratemyprofessors.com/paginate/professors/ratings?tid=" + str(professorId) + "&filter=&courseCode=&page=1")  # get request for page
        temp_jsonpage = json.loads(page.content)
        num_of_reviews = temp_jsonpage[
            'remaining'] + 20  # get total number of reviews
        return num_of_reviews


GeorgiaTech = RateMyProfScraper(361)
GeorgiaTech.GetProfessorDetail()
