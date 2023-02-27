from linkedin_api import Linkedin
import getpass
from functools import reduce

username = getpass.getpass(prompt='Email: ')
password = getpass.getpass(prompt='Password: ')
linkedin = Linkedin(username, password)

organizations = ['rothschild-cube', 'ourcrowd-llc', 'hilma-tech-for-impact', 'sdg-israel', 'cactus-capital', 'the-israeli-national-advisory-board-for-impact-investing', 'pitango-vc', 'innovalley-ltd', 'startup-nation-central', 'hanacoventures', 'tech-for-good', 'impact-first-investments', 'foodtech-israel', 'firstime-vc', 'edstart-edtech-hub', 'gfiisrael', 'the-kitchen-hub', 'conscious-capitalism-israel', 'hackaveret', '2bvc', 'fresh-start-foodtech-incubator-il', 'toniic', 'mindcet--ed-tech-innovation-center', 'masschallenge-israel', 'presentense', 'huji-innovate', 'rashi-foundation', 'microsoft', 'tau-ventures', 'health-il', 'bridges-israel', 'social-finance-israel', 'trendlines', 'our-generation-speaks', 'impact-idc', 'pears-program-for-global-innovation', 'a3i', 'max-initiative', 'desertech', 'arc-impact', '8200impact', 'amoon-fund', 'zora', 'edmond-rothschild-foundation-il', 'planetech-climate-tech-technologies', 'strauss-group', 'ecomotion-israel', 't3-technion-technology-transfer', 'growingil', 'gandyr-investments-group', 'impact-nation']
org_to_linked_orgs = {} # e.g., {alphabet: [Google, Facebook, Microsoft]}

for company in organizations[:4]:
    print(f'Calculating links for {company}...')
    records = linkedin.get_company_updates(company)
    get_attrs = lambda x: (x['value']['com.linkedin.voyager.feed.render.UpdateV2']['commentary']['text'].get('attributes', [])
                        if 'resharedUpdate' not in x['value']['com.linkedin.voyager.feed.render.UpdateV2'] else [])
    linked_orgs = reduce(lambda x, y: x + y,
                            [
                                [attr['miniCompany']['universalName'] for attr in get_attrs(r) 
                                                                        if attr['type'] == 'COMPANY_NAME']
                            for r in records],
                            [])
    org_to_linked_orgs[company] = linked_orgs 
    # debug print all linked_orgs that are in organizations
    print([org for org in linked_orgs if org in organizations])


# calculate org_pair_to_num_of_links to get the number of links from one org to another
org_pair_to_num_of_links = {}
for org, linked_orgs in org_to_linked_orgs.items():
    for linked_org in linked_orgs:
        if linked_org in organizations and not org == linked_org:
            org_pair_to_num_of_links[(org, linked_org)] = org_pair_to_num_of_links.get((org, linked_org), 0) + 1

print(org_pair_to_num_of_links)
