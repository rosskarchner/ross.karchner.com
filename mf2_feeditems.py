import mf2py
import mf2util
import json

from glob import glob

testcases = glob('test_cases/*.json')


def feeds_for_hentry(hentry):
    posttype = mf2util.post_type_discovery(hentry=hentry)
    feeds = {'feed#default', "feed#type:" + posttype}
    categories = [c.lower() for c in hentry['properties'].get('category', [])]
    for category in categories:
        feeds.add("feed#tag:" + category)
        feeds.add("feed#tag:"+category)
        feeds.add("feed#type:"+posttype + "#tag:" + category)

    return feeds



for testcase in testcases:
    print(testcase)
    feeds = feeds_for_hentry(hentry=json.load(open(testcase))['items'][0])
    print(feeds)