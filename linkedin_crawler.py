from linkedin_api import Linkedin
import getpass
from functools import reduce
import sys

username = 'amirsarid1@gmail.com'
password = getpass.getpass()
AAA = [b'firstime-vc', b'pitango-vc', b'trendlines', b'amoon-fund', b'impact-first-investments', b'bridges-israel', b'elahfund', b'zora', b'cactus-capital', b'israel-venture-network', b'arc-impact', b'good-company-mission-driven', b'gandyr-investments-group', b'champel-capital', b'menomadin-foundation', b'neweracp', b'terra-venture-partners', b'takwin-vc', b'morevc', b'vital-capital', b'micaventures', b'12635226', b'sibf-vc', b'kinneret-impact-ventures', b'bits-x-bites', b'shift-invest', b'2bvc', b'five-seasons-ventures', b'ngt-technology', b'jvp', b'28600695', b'hanacoventures', b'ourcrowd-llc', b'the-founders-kitchen', b'8vc']

company = sys.argv[-1]
linkedin = Linkedin(username, password)
records = linkedin.get_company_updates(company)
get_attrs = lambda x: (x['value']['com.linkedin.voyager.feed.render.UpdateV2']['commentary']['text'].get('attributes', [])
                       if 'resharedUpdate' not in x['value']['com.linkedin.voyager.feed.render.UpdateV2'] else [])
linked_company = reduce(lambda x, y: x + y,
                        [
                            [attr['miniCompany']['universalName'] for attr in get_attrs(r) if attr['type'] == 'COMPANY_NAME']
                        for r in records],
                        [])
print(company, len(set(linked_company)))
