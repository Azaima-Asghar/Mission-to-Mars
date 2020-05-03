
# Import Dependencies.
import pandas as pd
import time
# Import Splinter and BeautifulSoup.
from splinter import Browser
from bs4 import BeautifulSoup
import datetime as dt

# Set the executable path and initialize the chrome browser in splinter.
# executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
# browser = Browser('chrome', **executable_path)

# Function to initialize the browser.

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    # Set our news title and paragraph variables.
    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(browser),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
    # End the automated browsing session.
    browser.quit()

    return (data)
# ------ NEWS TITLE AND NEWS PARAGRAPH -------

# Function to scrape news title and paragraph.

def mars_news(browser):
    
    # Vist the mars nasa news site.
    url = ('https://mars.nasa.gov/news/')
    browser.visit(url)
    # Optional delay for loading page.
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time = 1)

    # Set up the HTML parser.
    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    # Add try/except for error handling.
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent element to find the first `a` tag and save it as `news_title`.
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the summary paragraph.
        news_p = slide_elem.find('div', class_ = 'article_teaser_body').get_text()

    except AttributeError:
        return (None, None)

    # Otherwise return news_title and new_p.
    return (news_title, news_p)

# ------ FEATURED IMAGES ------

# Function for featured images.

def featured_image(browser):

    # Visit url.
    url = ('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')
    browser.visit(url)

    # Find and click the full imagine button.
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Using Splinter’s ability to find elements using text.
    # Find the more info button and click it.
    browser.is_element_present_by_text('more info', wait_time = 1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup.
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except to handel errors.
    try:
        # Find the relative image url.
        img_url_rel = img_soup.select_one('figure.lede a img').get('src')

        # Use the base url to create an absolute url.
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    except AttributeError:
        return(None)

    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return (img_url)


# ----- FACTS ABOUT MARS -----

# Function for facts about Mars.

def mars_facts(browser):
    
    # Add try/except block to handel errors.
    try:
        # Instead of scraping each row, or the data in each <td />, we’re going to scrape the entire table 
        # with Pandas’ .read_html() function.
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return (None)
    
    # Assign columns and set index of dataframe.
    df.columns = ['Description', 'Values']
    df.set_index('Description', inplace = True)

    # Convert our DataFrame back into HTML-ready code using the .to_html() function.
    return (df.to_html(classes="table table-striped"))

def hemispheres(browser):

    # Visit url.
    url = ('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    browser.visit(url)

    mars_hemispheres = []

    # loop through the four tags and load the data into the dictonary.

    for i in range (4):
        time.sleep(5)
        images = browser.find_by_tag('h3')
        images[i].click()
        html = browser.html
        soup = BeautifulSoup(html, "html.parser")
        image_rel = soup.find('img', class_ = 'wide-image').get('src')
        image_title = soup.find('h2', class_ = 'title').get_text()
        image_url = f'https://astrogeology.usgs.gov/{image_rel}'
        dictonary = {"title": image_title, "image_url": image_url}
        mars_hemispheres.append(dictonary)
        browser.back()
            
    
    return (mars_hemispheres)

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())