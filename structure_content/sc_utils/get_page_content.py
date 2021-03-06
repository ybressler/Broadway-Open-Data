import sys
import re
import json
from bs4 import BeautifulSoup

sys.path.append('..')

# Custom stuff
from utils.string_manipulations import str_to_int, remove_special_chars


# ------------------------------------------------------------------------------

def get_title(soup, regex=True):
    """
    gets the title of the show

    ----
    If title is not available for the page, will look for h2 tag which has the show's
    title. (Developed heuristically...)
    """

    if not type(soup) == BeautifulSoup:
        return None # Error

    # Otherwise, proceed
    title = soup.head.title
    if title:
        title = title.text

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    elif regex:
        pattern = re.compile("(.*) Show")
        title = soup.body.find("h2", text=pattern)
        if not title:
            return None
        title = title.text
        title = pattern.search(title).group(1)
        return title

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    else:
        return None

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    if regex:
        pattern = re.compile("(.*) - [0-9]{4} Broadway")
        title_tmp = pattern.search(title)
        title = title_tmp.group(1) if title_tmp else title# If this breaks, will have to figure out why...

    # Finally
    return title

# ------------------------------------------------------------------------------

get_X_id = lambda x: str_to_int(re.search("theatre_id=([0-9]+)", x).group(1))

# ------------------------------------------------------------------------------

def get_production_info(soup):
    """gets all the data for the creative team"""

    data = {}
    if not type(soup) == BeautifulSoup:
        return data # Error

    # Get the title
    data["title"] = get_title(soup,regex=True)

    # Get table data
    more_data = get_table(soup, table_class="production-info")
    data.update(more_data)

    return data


# ------------------------------------------------------------------------------

def get_creative_info(soup):
    """gets all the data for the production"""

    data = {}
    if not type(soup) == BeautifulSoup:
        return data # Error

    # Get table data
    more_data = get_div_table(soup, table_class="staff")
    data.update(more_data)

    return data

# ------------------------------------------------------------------------------

def get_cast_info(soup):
    """gets all the data for the cast of the show"""

    data = {}
    if not type(soup) == BeautifulSoup:
        return data # Error

    # Get table data
    more_data = get_div_table(soup, table_class="staff")
    data.update(more_data)

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    # This creates a list of records – will result in nested data structure
    cast = []
    table = soup.body.find_all("div",{"class":"info"})
    for row in table:
        row_data ={}

        # Get the values one by one
        for key in ["name","role"]:
            # first the item
            value = row.find("div",{"class":key})
            value_text = value.text
            # then its href
            value_href = value.find("a",{"href":True})
            value_href = value_href["href"] if value_href else None
            # save to row data
            row_data.update({key:value_text, key+"_URL":value_href})
        # Save each row
        cast.append(row_data)
    # At the end, add to data
    data["cast"] = cast

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    return data

# ------------------------------------------------------------------------------

def get_table(soup, table_class):
    """gets coded tables from the webpage"""

    if not type(soup) == BeautifulSoup:
        return None # Error

    # Find all tables
    tables = soup.body.find_all("table", {"class":table_class})

    data = {}

    # Which table is which?
    for tb in tables:
        table_label = tb.find_previous_sibling("h2").text

        # This is the one we want
        if table_label.endswith("Show Information"):
            data["table_label"] = table_label
            tb_data = []

            for row in tb.find_all("tr"):
                row_vals = []

                # Read right to left
                for ele in row.find_all('td'):

                    # get the text
                    ele_text = remove_special_chars(ele.text.strip())

                    # Save your links
                    if ele.find("a"):
                        href = ele.find("a",{"href":True})["href"]
                        # Allow to place for theatre id
                        if re.search("theatre_id=[0-9]*",href):
                            tb_data.append(["theatre_id",href])
                        # Allow potential other urls...
                        else:
                            tb_data.append([ele_text+"_URL",href])

                    # Save the values from the row
                    row_vals.append(ele_text)

                # Save the row value
                if row_vals:
                    tb_data.append(row_vals)


            # ---------------------------------------------------------

            # Convert to a dict and save
            data.update(dict(tb_data))

        # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

        # Send them all out
        return data

# ------------------------------------------------------------------------------

# Use this function when scraping through the soup
def get_data_from_theatre_soup(soup):
    """
    returns table from soup
    """
    record = {}
    tables = soup.body.find_all("table", {"role":False})
    for tb in tables:
        table_label = tb.find_previous_sibling("h1")

        # Theater info table
        if table_label:

            # update the theater name
            record.update({"theatre name":table_label.text.strip()})
            for span in tb.find_all("span"):
                record.update({span.get("itemprop"):remove_special_chars(span.text.strip())})

            #Update the vals
            for row in tb.find_all("p"):
                row_key = remove_special_chars(row.find("strong").text.strip())
                row_val = remove_special_chars(row.find("strong").next_sibling.strip())
                record.update({row_key:row_val})
        else:
            # I don't want to parse the history of the theater...
            continue
    return record


# ------------------------------------------------------------------------------

def get_div_table(soup, table_class):
    """gets coded tables from the webpage"""

    if not type(soup) == BeautifulSoup:
        return None # Error

    # Find all tables
    tables = soup.body.find_all("div", {"class":table_class})

    data = {}

    # Which table is which?
    for tb in tables:
        tb_data = []

        table_label = tb.find_previous_sibling("h2").text
        data["table_label"] = table_label

        for row in tb.find_all("div"):

            row_vals = []
            # Read right to left
            for ele in row.find_all("span")[::-1]:

                # get the text
                ele_text = remove_special_chars(ele.text.strip())

                # Save your links
                if ele.find("a"):
                    href = ele.find("a",{"href":True})["href"]
                    tb_data.append([ele_text+"_URL",href])

                # Save the values from the row
                row_vals.append(ele_text)

            # Save the row value
            tb_data.append(row_vals)


        # Convert to a dict and save
        tb_data_dict = dict(tb_data)
        # Remove any blank keys
        tb_data_dict.pop('', None)
        # Update
        data.update(tb_data_dict)

    # -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    return data
