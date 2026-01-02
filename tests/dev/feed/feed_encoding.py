#! python3  # noqa: E265

# standard
import html

# 3rd party
import feedparser


# variables
GEOREZO_JOB_FEED = "https://georezo.net/extern.php?fid=10"
# GEOREZO_JOB_FEED = "tests/fixtures/rss/georezo_encoding_horrible.xml"

entry_index = 1
# expected_summary_ = 

# parse feed
feed = feedparser.parse(url_file_stream_or_string=GEOREZO_JOB_FEED)

print("Without escaping: ", feed.entries[entry_index].summary[:150])
print("Escaping 1 time: ", html.unescape(feed.entries[entry_index].summary)[:150])
print("Escaping 2 times: ", html.unescape(html.unescape(feed.entries[entry_index].summary))[:150])
print("Escaping 3 times: ", html.unescape(html.unescape(html.unescape(feed.entries[entry_index].summary)))[:150])
