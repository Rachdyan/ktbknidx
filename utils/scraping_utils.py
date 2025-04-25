
from bs4 import BeautifulSoup
import pandas as pd


def convert_from_info_div(info_div, keyword):

    try:
        stock_code = info_div.h6.span.get_text(strip=True)
    except Exception as e:
        print(f"No Stock Code Available because of {e}")
        stock_code = ''

    title = info_div.h6.get_text(strip=True)
    title = title.replace("/", " ")

    if (len(title) > 200):
        title = title[:200]

    raw_dt = info_div.time.get_text(strip=True).split('\n\t\t')

    month_map = {'Januari': '01', 'Februari': '02', 'Maret': '03',
                 'April': '04', 'Mei': '05', 'Juni': '06',
                 'Juli': '07', 'Agustus': '08', 'September': '9',
                 'Oktober': '10', 'November': '11', 'Desember': '12'}

    today_date = raw_dt[0]
    today_time = raw_dt[1]

    for month_str, n_month in month_map.items():
        today_date = today_date.replace(month_str, str(n_month))
        today_date = today_date.replace(" ", "-")

    main_link = [info_div.h6.a.get('href')]

    raw_list = info_div.ul.find_all('li')
    lampiran_link = [list.a.get('href') for list in raw_list]

    all_link = main_link + lampiran_link
    n_doc = len(all_link)

    result_dict = {'date': today_date, 'time': today_time, 'stock': stock_code,
                   'keyword': keyword, 'title': title.split(' [')[0],
                   'n_doc': n_doc, 'document_links': str(all_link)}

    result_df = pd.DataFrame([result_dict])

    return (result_df)


def scrape_data(sb, keyword, today_date, today_month_year):
    """
    Scrapes data from the IDX website for a given keyword.

    Args:
        sb: The SeleniumBase SB instance.
        keyword: The keyword to search for.
        today_date: The date to select.
        today_month_year: The month and year of the date.

    Returns:
        A pandas DataFrame containing the scraped data,
        or None if an error occurs.
    """

    try:
        print(f"Scraping {keyword}....")
        sb.open("https://www.idx.co.id/id/perusahaan-tercatat"
                "/keterbukaan-informasi/")
        sb.sleep(2)

        # html = sb.get_page_source()
        # print(html)
        sb.wait_for_element_present('#FilterSearch')
        sb.click('#FilterSearch')
        sb.send_keys('#FilterSearch', keyword)

        sb.sleep(1)
        sb.wait_for_element_present("input[name='date']")
        sb.click("input[name='date']")
        sb.sleep(1)

        first_calendar_header = sb.find_element(
            "div[class='mx-calendar-header']").text
        print(f"First calendar header: {first_calendar_header}")

        if today_month_year != first_calendar_header:
            sb.click("button[class='mx-btn mx-btn-text mx-btn-icon-left']")

        sb.sleep(2)

        print("Clicking Date")
        sb.wait_for_element_present(f"td[title = '{today_date}']")
        today_date_button = sb.find_element(f"td[title = '{today_date}']")
        today_date_button.click()
        today_date_button.click()

        sb.sleep(3)

        print("Getting Raw HTML")
        html = sb.get_page_source()
        soup = BeautifulSoup(html, 'html5lib')
        disclosure_tab = soup.find("div", class_='disclosure-tab')

        pagination_raw = disclosure_tab.find_all('span', recursive=False)[0]\
            .input
        max_page = int(pagination_raw['max'])
        print(f"Max page is {max_page}")

        # Handle potentially incorrect max_page (IDX quirk)
        if max_page == 58:
            sb.sleep(2)
            html = sb.get_page_source()
            soup = BeautifulSoup(html, 'html5lib')
            disclosure_tab = soup.find("div", class_='disclosure-tab')
            pagination_raw = disclosure_tab.find_all('span', recursive=False)
            [0].input
            max_page = int(pagination_raw['max'])
            print(f"Updated max page is {max_page}")

        result_df = pd.DataFrame()
        for current_page in range(1, max_page + 1):
            print((f"Getting data for keyword '{keyword}' from page "
                   f"{current_page}"))

            if current_page != 1:
                sb.click("button[class='btn-arrow --next']")
                sb.sleep(2)

                html = sb.get_page_source()
                soup = BeautifulSoup(html, 'html5lib')
                disclosure_tab = soup.find("div", class_='disclosure-tab')

            raw_info1 = disclosure_tab.find_all('div', recursive=False)[1].div
            raw_info2 = raw_info1.find_all('div', recursive=False)

            if len(raw_info2) > 1:
                try:
                    current_result = pd.concat(
                        [convert_from_info_div(x, keyword=keyword)
                         for x in raw_info2], ignore_index=True)
                except Exception as e:
                    print(f"Error processing multiple divs for keyword \
                          '{keyword}': {e}")
                    continue  # Go to the next page
            else:
                try:
                    current_result = convert_from_info_div(
                        raw_info2[0], keyword=keyword)
                except Exception as e:
                    print(f"Error processing single div for keyword \
                           '{keyword}': {e}")
                    continue  # Go to the next page

            result_df = pd.concat([result_df, current_result],
                                  ignore_index=True)
            print("Done Getting data for this keyword")

        return result_df

    except Exception as e:
        print(f"Error scraping data for keyword '{keyword}': {e}")
        return None  # Indicate failure


def truncate_with_ellipsis(text, max_length=100):
    """
    Truncates a string to a maximum length and appends '...' if it was
    truncated.

    Args:
        text: The input string.
        max_length: The maximum number of characters to keep before appending
        '...'.
                    Defaults to 100.

    Returns:
        The original string if its length is <= max_length, otherwise the
        truncated string followed by '...'. Returns None if input is not a
        string.
    """
    # Ensure input is a string
    if not isinstance(text, str):
        # Handle non-string input
        # (e.g., return None, empty string, or raise error)
        return None

    if len(text) > max_length:
        return text[:max_length] + "..."
    else:
        return text


def get_first_link(df):
    try:
        first_link = eval(df['document_links'])[0]
    except Exception as e:
        print(f"Error getting first link for {df['stock']} {e}")
        first_link = ''
    return first_link


def generate_message_string(df):
    try:
        msg_string = (f"•<b>{df['stock']}</b> - {df['time'].strftime('%H:%M')}"
                      f"- <a href='{df['first_link']}' target='_blank'>"
                      f"{truncate_with_ellipsis(df['title'], 75)}</a>")
    except Exception as e:
        print(f"Error getting message string for {df['stock']} {e}")
        msg_string = (f"•<b>{df['stock']}</b> - {df['time'].strftime('%H:%M')}"
                      f"{truncate_with_ellipsis(df['title'], 75)}")
    return msg_string
