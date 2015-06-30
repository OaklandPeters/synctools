"""
An attempt to download the CSS inline with the HTML, and parse it.

"""
import string
import random
import urllib2
import os




EXAMPLE_PHOTO_URL = 'http://127.0.0.1:8000/photo/2015/06/a-trip-around-the-solar-system/396872/'
RANDOM_NAME_LENGTH = 12


def create_random_name(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

def validate_for_existing_file(name):
    """ str -> str """
    if not os.path.exists(name):
        return name
    else:
        fname, fext = os.path.splitext(name)
        fullname = lambda postfix: os.path.join(fname, "-"+postfix, fext)
        postfix = "0"
        while (os.path.exists(fullname(postfix))):
            postfix = str(int(postfix)+1)
        return fullname(postfix)

def download_html(url, name=None):
    """ (str, Optional(str)) -> str
    Sideeffect: writes HTML file in current directory """
    if name is None:
        name = create_random_name(RANDOM_NAME_LENGTH) + ".html"
    name = validate_for_existing_file(name)
    response = urllib2.urlopen(url)
    page = response.read()


    print()
    print("page:", type(page), page)
    print()
    import ipdb
    ipdb.set_trace()
    print()
    

    with open(name, mode='w') as html_file:
        html_file.write(page)
    return name



def sync_css_images(url):

    name = download_html(url, 'testfile.html')


    print()
    print("name:", type(name), name)
    print()
    import ipdb
    ipdb.set_trace()
    print()
    


def main():
    """Run example code. In future, should take commandline arguments."""
    #return sync_page_images(example_url_1)
    return sync_css_images(EXAMPLE_PHOTO_URL)

if __name__ == "__main__":
    main()
