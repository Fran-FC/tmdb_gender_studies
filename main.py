from cmath import nan
import requests
import json 
import pandas as pd

api_key = "c1d23e87eceb35b0a722f750962ae337"


def get_year(date):
    return date.split("-")[0]

def valid_year(year):
  if year and year.isdigit():
    if int(year) >=1900 and int(year) <=2023:
      return year
    

def get_movie_id_by_title(title, year):
    url_search_movie = "https://api.themoviedb.org/3/search/movie?api_key={}&query={}"

    req = requests.get(url_search_movie.format(api_key, title))
    res = json.loads(req.content)

    id = None
    try:
        for m in res["results"]:
            if year:
                if get_year(m["release_date"]) == year:
                    id = m["id"]
                    break
        if not id:
            id = res["results"][0]["id"]
    except IndexError:
        print("id movie of {} not found".format(title))
    
    return id


def get_directors(id):
    url_search_credits = "https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits"
    req = requests.get(url_search_credits.format(id, api_key))
    res = json.loads(req.content)

    filter_res = list(filter(lambda x: x["job"] == "Director" and x["gender"] != 2, res["credits"]["crew"]))

    res = ""
    for i in range(len(filter_res)):
        director_entry = filter_res[i]
        res += "{}".format(director_entry["name"])
        if director_entry["gender"] == 0:
            res += " (genero desc.)"
        if i+1 < len(filter_res):
            res += " / "

    return res

def get_details(id):
    url_search_credits = "https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits"
    req = requests.get(url_search_credits.format(id, api_key))
    res = json.loads(req.content)

    return res


def get_duration(id): 
    json_details = get_details(id)

    try:
        return json_details["runtime"]
    except:
        return 0


if __name__=="__main__":
    try:
        df = pd.read_csv("peliculas_maria.csv", sep=";", encoding = "utf-8")
    except:
        df = pd.read_csv("peliculas_maria.csv", sep=";", encoding= "ISO-8859-1")

    index = 0
    for title in df.Title:
        if not valid_year(title[-4:]):
            year = nan
            title = title
        else:
            year = title[-4:]
            title = title[:-5] # remove last 5 digits (year and white space)

        id = get_movie_id_by_title(title, year)
        if id:
            director = get_directors(id) 
            duration = get_duration(id)

            df.at[index, "Director"] = director
            df.at[index, "Duration"] = duration
            df.at[index, "id"] = id
        else:             
            df.at[index, "Director"] = nan
            df.at[index, "Duration"] = nan
            df.at[index, "id"] = nan

        df.at[index, "Title"] = title
        df.at[index, "Year"] = year

        if not id or not director or not duration:
            print(df.loc[index, :])

        index += 1
    print(df)
    df.to_csv("result.csv", encoding="utf-8", index=False)