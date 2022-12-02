import requests
import re
import os
import pandas as pd
from datetime import date
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.dirname(__file__) + "/.env")


def raise_exception(var, msg):
    if var is None:
        raise ValueError(msg)


API_KEY, SEARCH_ENGINE_ID = os.environ["API_KEY"], os.environ["SEARCH_ENGINE_ID"]
raise_exception(API_KEY, "API_KEY not provided")
raise_exception(SEARCH_ENGINE_ID, "SEARCH_ENGINE_ID not provided")


def create_folder(folder=str(date.today()), dir=False):
    if not dir:
        folder = os.getcwd() + "\\" + folder
    else:
        folder = os.getcwd() + "\\" + str(dir) + "\\" + folder

    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def create_csv(data, dir, file=str(date.today()), file_type="csv"):
    header = list(data[0].keys())
    df = pd.DataFrame(data)

    file_name = dir + "\\" + file + "." + file_type
    if file_type == "csv":
        df.to_csv(file_name, encoding='utf-8', index=False, header=header)
    elif file_type == "xlsx":
        df.to_excel(file_name, encoding='utf-8', index=False, header=header)


def scrape(search_term, page_limit=11):
    page = 1
    # lists
    items = []

    while page < page_limit:
        # calculating start, (page=2) => (start=11), (page=3) => (start=21)
        start = (page - 1) * 10 + 1
        print(f"start: {start}, page: {page}, page_limit: {page_limit}")

        # constructing the URL
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_term}&start={start}"

        # save to csv file
        # filename = "result.csv"
        # csv_writer = csv.writer(open(filename, 'a', newline=''))
        # make the API request
        data = requests.get(url).json()

        # get the result items
        search_items = data.get("items")
        print(f"search items: {search_items}")

        # iterate over 10 results found
        try:
            for i, search_item in enumerate(search_items, start=1):
                # You may edit the regular expression as per your requirement
                # new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com",
                # data.text, re.I)) # re.I: (ignore case)
                # get the page title
                title = search_item.get("title")
                # page snippet
                snippet = search_item.get("snippet")
                # email
                email = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", snippet, re.I)
                # alternatively, you can get the HTML snippet (bolded keywords)
                # html_snippet = search_item.get("htmlSnippet")
                # extract the page url
                link = search_item.get("link")
                # print the results
                print("=" * 10, f"Result #{i + start - 1}", "=" * 10)
                print("Title:", title)
                print("Email:", email, str(type(email)))
                print("Description:", snippet)
                print("URL:", link, "\n")
                # save the data
                print("Inserting data....: {}".format(','.join(email)))
                # csv_writer.writerow(email)

                # Append result in items list
                items.append({
                    "Title": title,
                    "Email": ','.join(email),
                    "Description": snippet,
                    "URL": link,
                })
        except Exception as e:
            print(e)

        page = page + 1

    return items


if __name__ == "__main__":
    query = "lhr"
    res = scrape(query)
    directory = create_folder(dir="response")
    query = query.replace("\n", "-").replace(":", "")
    create_csv(res, directory, file=query, file_type="csv")
