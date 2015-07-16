"""Unit-tests for read_html."""
import os
import unittest

from .. import read_html_minimal
from .. import read_html
from .. import metafuncs


# stub_html_file = "example_article_page.html"
# example_file = "example_page_2.html"
# example_local_url = 'http://127.0.0.1:8000/photo/2015/06/a-trip-around-the-solar-system/396872/'
# example_src = '/media/img/mt/2015/06/rbow-1/lead_960.jpg?GE2DGNJVGE4DIMBVFYYA===='
# toc_url = 'http://127.0.0.1:8000/magazine/'

PROJECT_DIR = os.getcwd()
TEST_DIR = os.path.split(__file__)[0]
DATA_DIR = os.path.join(TEST_DIR, 'data')

EXAMPLE_HTML_FILE = os.path.join(DATA_DIR, "example_page_2.html")
EXAMPLE_LIVE_URL = ('http://theatlantic.com/international/archive/'
    '2015/07/iran-nuclear-weapons-deal-obama/398465/')


class TestMetafuncs(unittest.TestCase):

    """Unit-tests for some of the meta-functions.

    @todo: Move these to a seperate test file, so they can be refactored out with the metafuncs.
    """

    def test_getter(self):
        """Test get/getitem operators."""
        mydict = {'data-src': "MyPath", 'data-srcset': "pathset"}
        mydict_2 = {'data-srcset': "pathset"}
        maybe = metafuncs.maybe
        get = metafuncs.get
        getter = metafuncs.getitem

        get_src = maybe(get('src'),     # normal
                    maybe(get('data-src'),  # photo pages
                        maybe(get('data-srcset'))))  # home page

        _get_src = maybe(getter('src'),     # normal
                    maybe(getter('data-src'),  # photo pages
                        maybe(getter('data-srcset'))))  # home page

        self.assertEqual(get_src(mydict), "MyPath")
        self.assertEqual(_get_src(mydict), "MyPath")

        self.assertEqual(get_src(mydict_2), "pathset")
        self.assertEqual(_get_src(mydict_2), "pathset")

        mylist = ['a', 'bb', 'ccc']
        self.assertEqual(getter(1)(mylist), 'bb')
        self.assertRaises(AttributeError, get(1), mylist)


class TestReadHtmlMinimal(unittest.TestCase):

    """Test the minimalistic version of read_html."""

    library = read_html_minimal

    def test_srcs_local(self):
        """Test extracting src paths for images based on a local file."""
        results = self.library.get_img_srcs(EXAMPLE_HTML_FILE)

        expected = (
            '/media/img/mt/2015/06/rbow-1/hero_wide_640.jpg?GE2DGNJVGE4DIMBVFYYA====',
            '/media/img/mt/2015/06/truedetective15_11/hero_wide_640.jpg?GE2DGNJTGU4DGNBYFYYA====',
        )

        for line in expected:
            self.assertTrue(line in results)

    def test_srcs_remote(self):
        """Test extracting src paths for images based on a remote url."""
        expected = (
            'http://atlanticmedia.122.2o7.net/b/ss/atlanticprod/1/H.22--NS/0',
            'http://cdn.theatlantic.com/assets/media/img/issues/2015/06/09/0715_Cover/large.jpg',
            'http://cdn.theatlantic.com/assets/media/img/mt/2015/07/' +
            'RTR2DHZS/lead_960.jpg?GE2DGNRYG44TGOBVFYYA====',
        )
        results = self.library.get_img_srcs(EXAMPLE_LIVE_URL)
        for line in expected:
            self.assertTrue(line in results)

    def test_full(self):
        """Test main function / command-line interface function."""

        import pdb
        pdb.set_trace()
        print()

        read_html_minimal.main(EXAMPLE_LIVE_URL)
        self.library.main(EXAMPLE_LIVE_URL)


class TestReadHtml(TestReadHtmlMinimal):

    """Test the standard-Python version of read_html."""

    library = read_html

    # def test_full(self):
    #     """Dummy stub of testing the commandline interface."""
    #     pass
