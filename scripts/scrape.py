import json
import os
import pandas as pd
import time
from pytrends.request import TrendReq


def find_category(tree, name):
    if tree["name"] == name:
        return tree

    if "children" in tree.keys():
        for child in tree["children"]:
            node = find_category(child, name)
            if node:
                return node


def find_categories(tree, names):
    result = []
    if tree["name"] in names:
        result.append(tree)

    if "children" in tree.keys():
        for child in tree["children"]:
            result.extend(find_categories(child, names))

    return result


DATA_DIR = os.path.join("data")
MONTHLY_DIR = os.path.join(DATA_DIR, "monthly")

pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))

oecd_vars = dict()
cat_map = dict()

with open(os.path.join(DATA_DIR, "oecd_variables.json"), "r") as f:
    oecd_vars = json.load(f)

with open(os.path.join(DATA_DIR, "categories.json"), "r") as f:
    cat_map = json.load(f)

for key in oecd_vars["groups"].keys():
    if key in [
        "Crisis / Recession",
        "Unemployment / unemployment benefits",
        "Credit & Loans",
    ]:
        continue

    filename = key.replace(" ", "-").replace("/", "or")
    categories = find_categories(cat_map, oecd_vars["groups"][key])
    kw_list = [
        kw.strip()
        for kw in oecd_vars["groups"][key]
        if kw.strip() not in oecd_vars["categories"]
    ]

    print(key, kw_list, [cat["name"] for cat in categories])
    df = pd.DataFrame(columns=["date"] + kw_list + ["isPartial"])
    if len(categories) == 0:
        try:
            # monthly
            pytrends.build_payload(kw_list, cat=0, timeframe="all", geo="ID")
            df = pytrends.interest_over_time()
            # df = pytrends.get_historical_interest(
            #     kw_list,
            #     year_start=2004,
            #     month_start=1,
            #     day_start=1,
            #     hour_start=0,
            #     year_end=2023,
            #     month_end=1,
            #     day_end=1,
            #     hour_end=0,
            #     cat=0,
            #     geo="ID",
            #     sleep=0,
            # )
        except Exception as e:
            # df = pytrends.get_historical_interest(
            #     kw_list,
            #     year_start=2004,
            #     month_start=1,
            #     day_start=1,
            #     hour_start=0,
            #     year_end=2023,
            #     month_end=1,
            #     day_end=1,
            #     hour_end=0,
            #     cat=0,
            #     geo="ID",
            #     sleep=60,
            # )
            print(key, e)
        df.to_csv(os.path.join(MONTHLY_DIR, filename + ".csv"))
        time.sleep(60)
    else:
        for cat in categories:  # Needs tree traversal
            print(cat["name"])

            try:
                # monthly
                pytrends.build_payload(
                    kw_list, cat=cat["id"], timeframe="all", geo="ID"
                )
                df = pytrends.interest_over_time()
                # df = pytrends.get_historical_interest(
                #     kw_list,
                #     year_start=2004,
                #     month_start=1,
                #     day_start=1,
                #     hour_start=0,
                #     year_end=2023,
                #     month_end=1,
                #     day_end=1,
                #     hour_end=0,
                #     cat=cat["id"],
                #     geo="ID",
                #     sleep=0,
                # )
            except Exception as e:
                # df = pytrends.get_historical_interest(
                #     kw_list,
                #     year_start=2004,
                #     month_start=1,
                #     day_start=1,
                #     hour_start=0,
                #     year_end=2023,
                #     month_end=1,
                #     day_end=1,
                #     hour_end=0,
                #     cat=cat["id"],
                #     geo="ID",
                #     sleep=60,
                # )
                print(cat, e)

            filename = filename[:filename.find("_")] + "_" + str(cat["id"])
            df.to_csv(os.path.join(MONTHLY_DIR, filename + ".csv"), mode="a")
            time.sleep(2)

# indo_trending = pytrends.trending_searches(pn='indonesia')
# indo_trending.to_csv("indonesia_trending.csv")

# indo_top_2019 = pytrends.top_charts(2019, hl='en-US', tz=300, geo='ID')
# indo_top_2019.to_csv("indonesia_top_2019.csv")

# interest_ot = pytrends.interest_over_time()
# interest_ot.to_csv("interest_over_time")
