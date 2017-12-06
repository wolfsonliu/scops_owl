# ------------------
# Import Libraries
# ------------------
import os
import pandas as pd
# ------------------


# ------------------
# Import Functions
# ------------------
from scopsowl.query import get_affiliation_info
from scopsowl.fetch import fetch_doc
# ------------------

datadir = 'D:\\analysis\\scops_owl\\scopsowl'
the_affiliation_id = '60014966'  # "Jilin University" ID 60007711
the_api_keys = pd.read_csv(os.path.join(datadir, 'scopus_api_keys.txt'), header=0)['apikey']

university_info = get_affiliation_info(the_affiliation_id, the_api_keys[0])

university = pd.DataFrame(
    {
        'affiliation_id': [university_info['affiliation_id']],
        'eid': [university_info['eid']],
        'name': [university_info['affiliation_name']],
        'author': [university_info['author_count']],
        'document': [university_info['document_count']],
        'org_type': [university_info['org_type']],
        'org_domain': [university_info['org_domain']],
        'org_url': [university_info['org_url']],
        'address_country': [university_info['address_country']],
        'address_countryshort': [university_info['address_countryshort']],
        'address_state': [university_info['address_state']],
        'address_city': [university_info['address_city']],
        'address_part': [university_info['address_part']],
        'address_postalcode': [university_info['address_postalcode']]
    }
)

university.to_csv(os.path.join(datadir, 'university.csv'), index=False)

author = pd.read_csv(os.path.join(datadir, 'author.csv'), header=0)

the_author_ids = author['Auth-ID']
the_affiliation_ids = [the_affiliation_id] * author.shape[0]
# fetch data
fetched = fetch_doc(the_affiliation_ids[47777:], the_author_ids[47777:], 1949, ">", the_api_keys)
fetched['author_doc'].to_csv(os.path.join(datadir, 'author_doc.csv'), index=False)
fetched['document'].to_csv(os.path.join(datadir, 'document.csv'), index=False)
fetched['doc_affiliation'].to_csv(os.path.join(datadir, 'doc_affiliation.csv'), index=False)

# ------------------
# EOF
# ------------------
