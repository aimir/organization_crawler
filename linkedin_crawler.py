import datetime
from pprint import pprint
from linkedin_api import Linkedin
import getpass
import pickle
import os
from functools import reduce


organizations = ['rothschild-cube', 'ourcrowd-llc', 'hilma-tech-for-impact', 'sdg-israel', 'cactus-capital',
                 'the-israeli-national-advisory-board-for-impact-investing', 'pitango-vc', 'innovalley-ltd',
                 'startup-nation-central', 'hanacoventures', 'tech-for-good', 'impact-first-investments',
                 'foodtech-israel', 'firstime-vc', 'edstart-edtech-hub', 'gfiisrael', 'the-kitchen-hub',
                 'conscious-capitalism-israel', 'hackaveret', '2bvc', 'fresh-start-foodtech-incubator-il', 'toniic',
                 'mindcet--ed-tech-innovation-center', 'masschallenge-israel', 'presentense', 'huji-innovate',
                 'rashi-foundation', 'microsoft', 'tau-ventures', 'health-il', 'bridges-israel',
                 'social-finance-israel', 'trendlines', 'our-generation-speaks', 'impact-idc',
                 'pears-program-for-global-innovation', 'a3i', 'max-initiative', 'desertech', 'arc-impact',
                 '8200impact', 'amoon-fund', 'zora', 'edmond-rothschild-foundation-il',
                 'planetech-climate-tech-technologies', 'strauss-group', 'ecomotion-israel',
                 't3-technion-technology-transfer', 'growingil', 'gandyr-investments-group', 'impact-nation']


def get_records_by_org(organization_names, linkedin, recalculate=False, should_save_records=True):
    '''
    :param linkedin: A Linkedin object
    :param should_save_records: True if should save each and all records
    :param recalculate: True if should not load pickled records
    :param organization_names:
    :return: all company updates records from linkedin for each organization
    '''

    records_by_org = {}
    for org in organization_names:
        # continue if already have records for org, unless recalculate is True
        if not recalculate and f'records_{org}.pickle' in os.listdir():
            with open(f'records_{org}.pickle', 'rb') as f:
                records_by_org[org] = pickle.load(f)
            continue
        records = linkedin.get_company_updates(org, records=None)
        if should_save_records:
            with open(f'records_{org}.pickle', 'wb') as f:
                pickle.dump(records, f)
        records_by_org[org] = records

    return records_by_org


def get_attrs(x):
    try:
        return (x['value']['com.linkedin.voyager.feed.render.UpdateV2']['commentary']['text'].get('attributes', [])
                if 'resharedUpdate' not in x['value']['com.linkedin.voyager.feed.render.UpdateV2'] else [])
    except KeyError:
        return []


def get_org_and_linked_org_to_num_of_links_mapping(records_by_org):
    org_and_linked_org_to_num_of_links = {}

    for org, records in records_by_org.items():
        linked_orgs = reduce(lambda x, y: x + y, [[attr['miniCompany']['universalName'] for attr in get_attrs(r) if attr['type'] == 'COMPANY_NAME'] for r in records], [])
        for linked_org in linked_orgs:
            org_and_linked_org_to_num_of_links[(org, linked_org)] = org_and_linked_org_to_num_of_links.get((org, linked_org), 0) + 1

    with open(f'records_org_and_linked_org_to_num_of_links_mapping_{int(datetime.datetime.now().timestamp())}.pickle', 'wb') as f:
        pickle.dump(records, f)
    return org_and_linked_org_to_num_of_links


if __name__ == '__main__':
    username = getpass.getpass(prompt='Email: ')
    password = getpass.getpass(prompt='Password: ')
    linkedin = Linkedin(username, password, True, True)

    records_by_org = get_records_by_org(organizations, linkedin)
    org_and_linked_org_to_num_of_links_mapping = get_org_and_linked_org_to_num_of_links_mapping(records_by_org)
    pprint(org_and_linked_org_to_num_of_links_mapping)

