"""
Parsing GitLab API Request
A Josephs
13 May 2021
"""

# importing the load_dotenv from the python-dotenv module
from dotenv import load_dotenv
import os
import requests as r
from requests.exceptions import HTTPError
import csv


class Request:
    """ Get variables from .env file to preserve security,
    defaults to endpoint in env if not passed through main"""

    def __init__(self, endpoint=None):
        self.url = os.getenv('URL')
        self.team = os.getenv('TEAM')
        self.cookie = os.getenv('COOKIE')
        self.endpoint = endpoint if endpoint else os.getenv('ENDPOINT')
        self.request_str = self.build_request()
        self.raw_data = self.get_data()
        self.filtered_data = self.parse_data()

    def __str__(self):
        return "Request String: {} \n Data: {}".format(self.request_str, self.raw_data)

    def build_request(self):
        return "{}{}{}".format(self.url, self.team, self.endpoint)

    def get_data(self):
        """ Request returns data in the form:
        endpoint pipelines:
        {id: , sha: , ref: , status: , created_at: , updated_at: ,web_url: ,}
        """
        page = 1
        response_builder = []

        try:
            my_headers = {"Cookie": self.cookie}
            flag = True

            while flag:
                req = self.request_str + "?per_page=100&page=" + str(page)
                page += 1

                response = r.get(req, headers=my_headers)
                response.raise_for_status()
                response_json = response.json()

                response_builder += response_json

                if len(response.text) == 2:
                    flag = False

            return response_builder

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        except Exception as err:
            print(f'Other error occurred: {err}')

    def parse_data(self):
        """ Get three values:
        endpoint
        pipelines:
        {id:, ref:, status:, created_at: ,}
        """
        filtered_data = []
        for task in self.raw_data:
            filtered_data.append((task['id'], task['ref'], task['status'], task['created_at']))
        return filtered_data


def write_to_csv(request):
    with open('request_data.csv', 'w', newline='') as csvfile:
        request_writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        request_writer.writerow(["ID", "REF", "STATUS", "DATE"])

        for _id, ref, status, date in request.filtered_data:
            request_writer.writerow([_id, ref, status, date])


def print_json(json_response):
    for each in json_response:
        print(each["id"])


def main():
    load_dotenv('.env')
    new_request = Request()
    write_to_csv(new_request)
    # print_json(new_request.raw_data)


if __name__ == '__main__':
    main()
