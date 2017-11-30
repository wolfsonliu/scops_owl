# ------------------
# Libraries
# ------------------
import pandas as pd
# ------------------

# ------------------
# Functions
# ------------------
from queryscopus import get_affiliation_info
from queryscopus import search_document
from queryscopus import makequery_affiliation_id
from queryscopus import makequery_author_id
# ------------------

# ------------------
# Errors
# ------------------
from queryscopus import QuotaExceededError
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError
from urllib3.exceptions import NewConnectionError
# ------------------

affiliation_id = '60014966'
api_key = pd.read_csv('scopuskeys.txt', header=0)['apikey']

university_info = get_affiliation_info(affiliation_id, api_key[0])

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

university.to_csv('university.csv', index=False)

author = pd.read_csv('author.csv', header=0)

def fetch_doc(affiliation_id, author_ids, api_keys):
    pass

author_doc = list()  # author_id, scopus_id

document = list()  # scopus_id, title, eid, dc:creator, citedby_count

doc_affiliation = list()  # scopus_id, affiliation_name, affiliation_city, affiliation_country

i = 0

try:
    for author_id in author['Auth-ID']:
        start = 0
        whileloop = True
        while whileloop:
            try:
                # fetch document information
                doc_info = search_document(
                    makequery_author_id(author_id) + makequery_affiliation_id(affiliation_id),
                    start, 200, api_key[i]
                )
            except QuotaExceededError:
                i += 1
                doc_info = search_document(
                    makequery_author_id(author_id) + makequery_affiliation_id(affiliation_id),
                    start, 200, api_key[i]
                )
            start += 200
            if int(doc_info['total_count']) == 0:
                whileloop = False
                continue
            # store author document information

            author_doc.extend(
                list(
                    zip(
                        [author_id] * len(doc_info['documents']),
                        [
                            x['dc:identifier'] if 'dc:identifier' in x else x['dc:title'] for x in
                            doc_info['documents']
                        ]
                    )
                )
            )

            # store document information
            document.extend(
                list(
                    zip(
                        [x['dc:identifier'] if 'dc:identifier' in x else '' for x in doc_info['documents']],
                        [x['article-number'] if 'article-number' in x else '' for x in doc_info['documents']],
                        [x['dc:title'] if 'dc:title' in x else '' for x in doc_info['documents']],
                        [x['eid'] if 'eid' in x else '' for x in doc_info['documents']],
                        [x['citedby-count'] if 'citedby-count' in x else '' for x in doc_info['documents']],
                        [x['dc:creator'] if 'dc:creator' in x else '' for x in doc_info['documents']],
                        [x['prism:aggregationType'] if 'prism:aggregationType' in x else '' for x in doc_info['documents']],
                        [x['prism:coverDate'] if 'prism:coverDate' in x else '' for x in doc_info['documents']],
                        [x['prism:coverDisplayDate'] if 'prism:coverDisplayDate' in x else '' for x in doc_info['documents']],
                        [x['prism:doi'] if 'prism:doi' in x else '' for x in doc_info['documents']],
                        [x['prism:eIssn'] if 'prism:eIssn' in x else '' for x in doc_info['documents']],
                        [x['prism:issn'] if 'prism:issn' in x else '' for x in doc_info['documents']],
                        [x['prism:issueIdentifier'] if 'prism:issueIdentifier' in x else '' for x in doc_info['documents']],
                        [x['prism:pageRange'] if 'prism:pageRange' in x else '' for x in doc_info['documents']],
                        [x['prism:publicationName'] if 'prism:publicationName' in x else '' for x in doc_info['documents']],
                        [x['prism:url'] if 'prism:url' in x else '' for x in doc_info['documents']],
                        [x['prism:volume'] if 'prism:volume' in x else '' for x in doc_info['documents']],
                        [x['subtype'] if 'subtype' in x else '' for x in doc_info['documents']],
                        [x['subtypeDescription'] if 'subtypeDescription' in x else '' for x in doc_info['documents']],
                    )
                )
            )

            # store document affiliation information
            doc_affiliation_dict = dict(
                zip(
                    [x['dc:identifier'] if 'dc:identifier' in x else x['article_number'] for x in doc_info['documents'] if
                     'affiliation' in x],
                    [x['affiliation'] for x in doc_info['documents'] if 'affiliation' in x]
                )
            )

            for x, y in doc_affiliation_dict.items():
                doc_affiliation.extend(
                    list(
                        zip(
                            [x] * len(y),
                            [z['affilname'] for z in y],
                            [z['affiliation-city'] for z in y],
                            [z['affiliation-country'] for z in y]
                        )
                    )
                )

            totalcount = int(doc_info['total_count'])
            if start >= totalcount:
                whileloop = False
except (ConnectionError, NewConnectionError, MaxRetryError):
    # if the network has problem, record the id of author
    with open('brokenauthorid.txt', 'w') as f:
        f.write('Author {0:d} stopped.\n'.format(author_id))
finally:
    df_author_doc = pd.DataFrame(author_doc)
    df_author_doc.columns = ['author_id', 'scopus_id']
    df_author_doc.to_csv('author_doc.csv', index=False)
    df_document = pd.DataFrame(document)
    df_document.columns = [
        'scopus_id', 'article_number', 'title', 'eid', 'citedby_count', 'creator', 'aggregationType',
        'coverDate', 'coverDisplayDate', 'doi', 'eIssn', 'issn', 'issueIdentifier', 'pageRange', 'publication',
        'url', 'volume', 'subtype', 'subtype_description'
    ]
    df_document.to_csv('document.csv', index=False)
    df_doc_affiliation = pd.DataFrame(doc_affiliation)
    df_doc_affiliation.columns = ['scopus_id', 'affiliation_name', 'affiliation_city', 'affiliation_country']
    df_doc_affiliation.to_csv('doc_affiliation.csv', index=False)



