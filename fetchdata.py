# ------------------
# Import Libraries
# ------------------
import pandas as pd
import time
# ------------------

# ------------------
# Import Functions
# ------------------
from queryscopus import get_affiliation_info
from queryscopus import get_document
from queryscopus import search_document
from queryscopus import make_query_affiliation_id
from queryscopus import make_query_author_id
# ------------------

# ------------------
# Errors
# ------------------
from queryscopus import QuotaExceeded
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError
from urllib3.exceptions import NewConnectionError


class UnmatchedLengthError(ValueError):
    pass


class NoAvailableKeys(ValueError):
    pass
# ------------------

# ------------------
# Functions
# ------------------


def fetch_affiliation_info(affiliation_ids, api_keys):
    if not (hasattr(affiliation_ids, '__getitem__') and hasattr(affiliation_ids, '__iter__')):
        raise ValueError('affiliation_ids should be list-like object.')
    if not (hasattr(api_keys, '__getitem__') and hasattr(api_keys, '__iter__')):
        raise ValueError('api_keys should be list-like object.')
    aff_info = list()
    try:
        api_key_i = 0
        for affiliation_id in affiliation_ids:
            quota_while = True
            while quota_while:
                try:
                    aff = get_affiliation_info(affiliation_id, api_keys[api_key_i])
                    quota_while = False
                except QuotaExceeded:
                    api_key_i += 1
                    if api_key_i == len(api_keys):
                        raise NoAvailableKeys('Usable key exhausted.')
            aff_info.append(aff)
    except (ConnectionError, NewConnectionError, MaxRetryError):
        # if the network has problem, record the id of author and affiliation
        with open('fetch_affiliation_info_broken.txt', 'w') as f:
            f.write('Affiliation {0} stopped.\n'.format(affiliation_id))
    finally:
        result = pd.DataFrame(aff_info)
        return result


def fetch_document_info(scopus_ids, api_keys):
    if not (hasattr(scopus_ids, '__getitem__') and hasattr(scopus_ids, '__iter__')):
        raise ValueError('affiliation_ids should be list-like object.')
    if not (hasattr(api_keys, '__getitem__') and hasattr(api_keys, '__iter__')):
        raise ValueError('api_keys should be list-like object.')
    doc_info = dict()
    doc_info['document'] = list()
    doc_info['author'] = list()
    doc_info['subject_area'] = list()
    try:
        api_key_i = 0
        for scopus_id in scopus_ids:
            quota_while = True
            while quota_while:
                try:
                    doc = get_document(scopus_id, api_keys[api_key_i])
                    quota_while = False
                except QuotaExceeded:
                    api_key_i += 1
                    if api_key_i == len(api_keys):
                        raise NoAvailableKeys('Usable key exhausted.')
            doc_info['document'].append(doc['document'])
            doc_info['subject_area'].extend(doc['subject_area'])
            doc_info['author'].extend(doc['author'])
    except (ConnectionError, NewConnectionError, MaxRetryError):
        # if the network has problem, record the id of author and affiliation
        with open('fetch_document_info_broken.txt', 'w') as f:
            f.write('Document {0} stopped.\n'.format(doc['document']['scopus_id']))
    finally:
        result = dict()
        result['document'] = pd.DataFrame(doc_info['document'])
        result['subject_area'] = pd.DataFrame(doc_info['subject_area'])
        result['author'] = pd.DataFrame(doc_info['author'])
        return result


def fetch_doc(affiliation_ids, author_ids, api_keys):
    # input variables validation
    if not (hasattr(affiliation_ids, '__getitem__') and hasattr(affiliation_ids, '__iter__')):
        raise ValueError('affiliation_ids should be list-like object.')
    if not (hasattr(author_ids, '__getitem__') and hasattr(author_ids, '__iter__')):
        raise ValueError('author_ids should be list-like object.')
    if not (hasattr(api_keys, '__getitem__') and hasattr(api_keys, '__iter__')):
        raise ValueError('api_keys should be list-like object.')
    if len(affiliation_ids) != len(author_ids):
        raise UnmatchedLengthError('The length of affiliation_ids and author_ids should be the same.')
    # make store list
    author_doc = list()  # author_id, scopus_id
    document = list()  # scopus_id, title, eid, dc:creator, citedby_count
    doc_affiliation = list()  # scopus_id, affiliation_name, affiliation_city, affiliation_country
    api_key_i = 0
    try:
        for author_id, affiliation_id in zip(author_ids, affiliation_ids):
            start = 0
            while_loop = True
            while while_loop:
                quota_while = True
                # api_key quota check
                while quota_while:
                    try:
                        # fetch document information
                        # scopus search,         20000
                        doc_info = search_document(
                            make_query_author_id(author_id) + make_query_affiliation_id(affiliation_id),
                            start, 200, api_keys[api_key_i]
                        )
                        quota_while = False
                    except QuotaExceeded:
                        # deal with the api key running out of quota
                        # quota will be refreshed per week
                        # series title,          20000
                        # citations count,       50000
                        # citations overview,    20000
                        # abstract retrieval,    10000
                        # affiliation retrieval,  5000
                        # author retrieval,       5000
                        # affiliation search,     5000
                        # author search,          5000
                        # scopus search,         20000
                        api_key_i += 1
                        if api_key_i == len(api_keys):
                            raise NoAvailableKeys('Usable key exhausted.')

                start += 200
                if int(doc_info['total_count']) == 0:
                    while_loop = False
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
                            [
                                x['dc:identifier'] if 'dc:identifier' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['article-number'] if 'article-number' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['dc:title'] if 'dc:title' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['eid'] if 'eid' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['citedby-count'] if 'citedby-count' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['dc:creator'] if 'dc:creator' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['prism:aggregationType'] if 'prism:aggregationType' in x else ''
                                for x in doc_info['documents']
                            ],
                            [
                                x['prism:coverDate'] if 'prism:coverDate' in x else ''
                                for x in doc_info['documents']
                            ],
                            [
                                x['prism:coverDisplayDate'] if 'prism:coverDisplayDate' in x else ''
                                for x in doc_info['documents']
                            ],
                            [
                                x['prism:doi'] if 'prism:doi' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['prism:eIssn'] if 'prism:eIssn' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['prism:issn'] if 'prism:issn' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['prism:issueIdentifier'] if 'prism:issueIdentifier' in x else ''
                                for x in doc_info['documents']
                            ],
                            [
                                x['prism:pageRange'] if 'prism:pageRange' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['prism:publicationName'] if 'prism:publicationName' in x else ''
                                for x in doc_info['documents']
                            ],
                            [
                                x['prism:url'] if 'prism:url' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['prism:volume'] if 'prism:volume' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['subtype'] if 'subtype' in x else '' for x in doc_info['documents']
                            ],
                            [
                                x['subtypeDescription'] if 'subtypeDescription' in x else ''
                                for x in doc_info['documents']
                            ],
                        )
                    )
                )

                # store document affiliation information
                doc_affiliation_dict = dict(
                    zip(
                        [
                            x['dc:identifier'] if 'dc:identifier' in x else x['article_number']
                            for x in doc_info['documents'] if 'affiliation' in x
                        ],
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
                # stop the loop if all the record fetched
                total_count = int(doc_info['total_count'])
                if start >= total_count:
                    while_loop = False
    except (ConnectionError, NewConnectionError, MaxRetryError):
        # if the network has problem, record the id of author and affiliation
        with open('fetch_doc_broken.txt', 'a') as f:
            f.write(
                ' '.join(
                    [
                        time.strftime("%Y-%m-%d %H:%M"),
                        'Affiliation {0} Author {1} stopped.\n'.format(affiliation_id, author_id)
                     ]
                )
            )
    finally:
        # change list to DataFrame
        df_author_doc = pd.DataFrame(author_doc)
        df_author_doc.columns = ['author_id', 'scopus_id']
        df_document = pd.DataFrame(document)
        df_document.columns = [
            'scopus_id', 'article_number', 'title', 'eid', 'citedby_count', 'creator', 'aggregationType',
            'coverDate', 'coverDisplayDate', 'doi', 'eIssn', 'issn', 'issueIdentifier', 'pageRange', 'publication',
            'url', 'volume', 'subtype', 'subtype_description'
        ]
        df_doc_affiliation = pd.DataFrame(doc_affiliation)
        df_doc_affiliation.columns = ['scopus_id', 'affiliation_name', 'affiliation_city', 'affiliation_country']
        result = dict()
        result['author_doc'] = df_author_doc
        result['document'] = df_document
        result['doc_affiliation'] = df_doc_affiliation
        return result

# ------------------


the_affiliation_id = '60014966'  # "Jilin University" ID 60007711
the_api_keys = pd.read_csv('scopuskeys.txt', header=0)['apikey']

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

university.to_csv('university.csv', index=False)

author = pd.read_csv('author.csv', header=0)

the_author_ids = author['Auth-ID']
the_affiliation_ids = [the_affiliation_id] * author.shape[0]
# fetch data
fetched = fetch_doc(the_affiliation_ids[13849:], the_author_ids[13849:], the_api_keys)
fetched['author_doc'].to_csv('author_doc.csv', index=False)
fetched['document'].to_csv('document.csv', index=False)
fetched['doc_affiliation'].to_csv('doc_affiliation.csv', index=False)

# ------------------
# EOF
# ------------------
