import datetime
from pprint import pprint
from linkedin_api import Linkedin
import getpass
import pickle
import os
from functools import reduce


organizations = ['2bvc', 'amoon-fund', 'arc-impact', 'bridges-israel', 'capital-nature', 'champel-capital',
                 'firstime-vc', 'good-company-mission-driven', 'jvp', 'kmai-capital', 'morevc', 'nevateam',
                 'neweracp', 'ourcrowd-llc', 'pitango-vc', 'rhodium', 'takwin-vc', 'terra-venture-partners',
                 'the-founders-kitchen', 'trendlines', 'wonder-ventures-capital-management', 'zora',
                 'cactus-capital', 'realityinvestmentfund', 'chw', 'edmond-rothschild-foundation-il',
                 'rashi-foundation', 'ujia', 'gandyr-investments-group', 'keren-hayesod---uia', 'leichtag-foundation',
                 'menomadin-foundation', 'merage-foundation-israel', 'the-portland-tlv', 'ruderman-family-foundation',
                 'the-jewish-federation-of-greater-los-angeles', 'the-russell-berrie-foundation',
                 'tmura---the-israeli-public-service-venture-fund', 'uja-federation-of-new-york', 'yad-hanadiv',
                 'value-2-responsible-investment-house', 'vintage-investment-partners', 'vital-capital',
                 'bird-foundation', 'theellafund', 'israelinnovationauthority', 'israel-venture-network', 'jimpact',
                 'kinneret-impact-ventures', 'menomadin-foundation', 'israel-free-loan-association',
                 u'start-החטיבה-לחדשנות-טכנולוגית-במשרד-החינוך', 'hilma-tech-for-impact', 'max-initiative', 'unistream',
                 'rothschild-cube',
                 'kayama-executive-education-centre-for-social-innovation-and-impact-entrepreneurship\u200f',
                 'social-finance-israel', 'milkeninnovationcenter', 'erasmus-ifi-innovative-finance-inclusion',
                 'rise-impact-mta', 'maala', 'startup-nation-central', 'tech-for-good',
                 'm-a-program-in-migration-studies-at-tel-aviv-university', 'yazamut360',
                 'bar-ilan-centre-for-smart-cities', 'esil-environmental-sustainability-innovation-lab',
                 'galil-ofek-ventures', 'huji-innovate', 'innovalley-ltd', 'the-peres-center-for-peace',
                 'knowledge-center-for-innovation', 'fresh-start-foodtech-incubator-il', 'medx-xelerator-lp',
                 'mindup-ltd.', 'our-generation-speaks', 'the-kitchen-hub', 'conscious-capitalism-israel', 'jdc',
                 'google', 'the-israeli-national-advisory-board-for-impact-investing', u'ציונות-2000', 'istipi',
                 'imagine-impact-consulting', 'israel-impact-partners', 'weave-impact', '8400-the-health-network',
                 'strauss-group', 'desertech', 'ecomotion-israel', 'the-gita', 'growingil', 'hasoub', 'health-il',
                 'igtsil', 'impact-nation', 'lavan', 'planetech-climate-tech-technologies', 'sdg-israel', 'gfiisrael',
                 'israeli-smart-energy-association', 'toniic', 'impact-51', 'michal-sela-forum',
                 'mindcet--ed-tech-innovation-center', 'pears-program-for-global-innovation', '8200impact', 'a3i',
                 'aion-labs', 'dana-lp', 'edstart-edtech-hub', 'hackaveret', 'masschallenge-israel', 'presentense',
                 'the-kitchen-hub', 'code-for-israel', u'המרכז-להתייעלות-במשאבים', 'lin-health', 'amai-proteins',
                 'addionics', 'agritask', 'iluria-ltd', 'keheala', 'riseupisrael']


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
    # remove all org_and_linked_org pairs that are not in organizations
    org_and_linked_org_to_num_of_links_mapping = {k: v for k, v in org_and_linked_org_to_num_of_links_mapping.items() 
                                                  if k[0] in organizations and k[1] in organizations and k[0] != k[1]}
    pprint(org_and_linked_org_to_num_of_links_mapping)

