# ------------------
# Import Libraries
# ------------------
import time
import logging
import pandas as pd


# ------------------
# Import Functions and Classes
# ------------------
from scopsowl.query import get_affiliation_info
from scopsowl.query import get_document_info
from scopsowl.query import get_author_info
from scopsowl.query import search_document
from scopsowl.query import make_query_affiliation_id
from scopsowl.query import make_query_author_id
from scopsowl.query import make_query_pubyear


# ------------------
# Errors and logs
# ------------------
from scopsowl.query import QuotaExceeded
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError, NewConnectionError


class UnmatchedLengthError(ValueError):
    pass


class NoAvailableKeys(ValueError):
    pass


logger = logging.getLogger('scops_owl.fetch')


# ------------------
# Functions
# ------------------
def fetch_affiliation_info(affiliation_ids, api_keys):
    if not (hasattr(affiliation_ids, '__getitem__') and hasattr(affiliation_ids, '__iter__')):
        raise ValueError('affiliation_ids should be list-like object.')
    if not (hasattr(api_keys, '__getitem__') and hasattr(api_keys, '__iter__')):
        raise ValueError('api_keys should be list-like object.')
    aff_info = list()
    affiliation_id = 'none'
    try:
        api_key_i = 0
        for affiliation_id in affiliation_ids:
            logger.debug('fetch_affiliation_info(): affiliation_id {0}'.format(affiliation_id))
            # change api key if api key is out of Quota
            quota_while = True
            while quota_while:
                try:
                    aff = get_affiliation_info(affiliation_id, api_keys[api_key_i])
                    logger.info(' '.join(['获取单位：', aff['affiliation-name']]))
                    aff_basic = {
                        'affiliation_id': affiliation_id,
                        'affiliation_name': aff['affiliation-name'] if 'affiliation-name' in aff else '',
                        'address': aff['address'] if 'address' in aff else '',
                        'city': aff['city'] if 'city' in aff else '',
                        'country': aff['country'] if 'country' in aff else '',
                        'eid': aff['coredata']['eid'] if 'eid' in aff['coredata'] else '',
                        'author_count': aff['coredata']['author-count'] if 'author-count' in aff['coredata'] else '',
                        'document_count': aff['coredata']['document-count']
                        if 'document-count' in aff['coredata'] else '',
                        'type': aff['profile']['org-type'] if 'org-type' in aff['profile'] else '',
                        'domain': aff['profile']['org-domain'] if 'org-domain' in aff['profile'] else '',
                        'url': aff['profile']['org-url'] if 'org-url' in aff['profile'] else ''
                    }
                    logger.debug(
                        'fetch_affiliation_info(): get_affiliation_info result aff {0}'.format(
                            aff_basic['affiliation_name']
                        )
                    )
                    aff_info.append(aff_basic)
                    quota_while = False
                except QuotaExceeded:
                    api_key_i += 1
                    if api_key_i == len(api_keys):
                        raise NoAvailableKeys('Usable key exhausted.')
    except (ConnectionError, NewConnectionError, MaxRetryError):
        # if the network has problem, record the id of author and affiliation
        with open('fetch_affiliation_info_broken.txt', 'w') as f:
            f.write('Affiliation {0} stopped.\n'.format(affiliation_id))
    finally:
        result = pd.DataFrame(aff_info)
        return result

# ------------------


def fetch_author_info(author_ids, api_keys):
    if not (hasattr(author_ids, '__getitem__') and hasattr(author_ids, '__iter__')):
        raise ValueError('author_ids should be list-like object.')
    if not (hasattr(api_keys, '__getitem__') and hasattr(api_keys, '__iter__')):
        raise ValueError('api_keys should be list-like object.')
    au_info = dict()
    au_info['author'] = list()
    au_info['affiliation'] = list()
    au_info['subject_area'] = list()
    author_id = 'none'
    i = 1
    total_number = len(author_ids)
    try:
        api_key_i = 0
        for author_id in author_ids:
            quota_while = True
            while quota_while:
                try:
                    au = get_author_info(author_id, api_keys[api_key_i])
                    quota_while = False
                    au_core = dict()
                    au_core['author_id'] = au['coredata']['dc:identifier']
                    au_core['eid'] = au['coredata']['eid']
                    au_core['document_count'] = au['coredata'][
                        'document-count'
                    ] if 'document-count' in au['coredata'] else ''
                    au_core['cited_by_couunt'] = au['coredata'][
                        'cited-by-count'
                    ] if 'cited-by-count' in au['coredata'] else ''
                    au_core['citation_count'] = au['coredata'][
                        'citation-count'
                    ] if 'citation-count' in au['coredata'] else ''
                    au_core['affiliation_current'] = au['affiliation-current'][
                        '@id'
                    ] if '@id' in au['affiliation-current'] else ''
                    au_core['surname'] = au['author-profile']['preferred-name']['surname']
                    au_core['idxname'] = au['author-profile']['preferred-name']['indexed-name']
                    au_core['initialname'] = au['author-profile']['preferred-name']['initials']
                    au_core['givenname'] = au['author-profile']['preferred-name']['given-name']
                    logger.debug(' '.join(['获取作者：', ', '.join([au_core['surname'], au_core['givenname']])]))
                    # history affiliation information of author
                    au_affiliation = list()
                    if 'affiliation-history' in au['author-profile']:
                        if isinstance(au['author-profile']['affiliation-history']['affiliation'], dict):
                            au_affiliation.append(
                                {
                                    'author_id': str(author_id),
                                    'affiliation_id': au['author-profile']['affiliation-history']['affiliation'][
                                        '@affiliation-id'
                                    ] if '@affiliation-id' in au['author-profile'][
                                        'affiliation-history'
                                    ]['affiliation'] else '',
                                    'parent_id': au['author-profile']['affiliation-history']['affiliation'][
                                        '@parent'
                                    ] if '@parent' in au['author-profile'][
                                        'affiliation-history'
                                    ]['affiliation'] else '',
                                    'affiliation_name': au['author-profile']['affiliation-history']['affiliation'][
                                        'ip-doc'
                                    ]['preferred-name']['$'],
                                    'parent_name': au['author-profile']['affiliation-history']['affiliation'][
                                         'ip-doc'
                                    ]['parent-preferred-name']['$'],
                                    'affiliation_city': au['author-profile']['affiliation-history']['affiliation'][
                                        'ip-doc'
                                    ]['address']['city'],
                                    'affiliation_state': au['author-profile']['affiliation-history']['affiliation'][
                                        'ip-doc'
                                    ]['address']['state'],
                                    'affiliation_country': au['author-profile']['affiliation-history']['affiliation'][
                                        'ip-doc'
                                    ]['address']['country'],
                                    'affiliation_zipcode': au['author-profile']['affiliation-history']['affiliation'][
                                        'ip-doc'
                                    ]['address']['postal-code'],
                                    'affiliation_address': au['author-profile']['affiliation-history']['affiliation'][
                                        'ip-doc'
                                    ]['address']['address-part'],
                                    'affiliation_type': au['author-profile']['affiliation-history']['affiliation'][
                                        'ip-doc'
                                    ]['@type'],
                                }
                            )
                        elif isinstance(au['author-profile']['affiliation-history']['affiliation'], list):
                            au_affiliation.extend(
                                [
                                    {
                                        'author_id': str(author_id),
                                        'affiliation_id': x['@affiliation-id'] if '@affiliation-id' in x else '',
                                        'parent_id': x['@parent'] if '@parent' in x else '',
                                        'affiliation_name': x['ip-doc']['preferred-name']['$'],
                                        'parent_name': x['ip-doc']['parent-preferred-name']['$'],
                                        'affiliation_city': x['ip-doc']['address']['city'],
                                        'affiliation_state': x['ip-doc']['address']['state'],
                                        'affiliation_country': x['ip-doc']['address']['country'],
                                        'affiliation_zipcode': x['ip-doc']['address']['postal-code'],
                                        'affiliation_address': x['ip-doc']['address']['address-part'],
                                        'affiliation_type':x['ip-doc']['@type'],
                                    } for x in au['author-profile']['affiliation-history']['affiliation']
                                ]
                            )
                    logger.debug(
                        'fetch_author_info: loop au_affiliation affiliation_name: {0}'.format(
                            au_affiliation[0]['affiliation_name']
                        )
                    )
                    # author information of document
                    au_area = list()
                    if 'subject-areas' in au:
                        if isinstance(au['subject-areas']['subject-area'], dict):
                            au_area.append(
                                {
                                    'author_id': str(author_id),
                                    'code': au['subject-areas']['subject-area']['code'],
                                    'abbrev': au['subject-areas']['subject-area']['abbrev'],
                                    'subject_area':  au['subject-areas']['subject-area']['$']
                                }
                            )
                        elif isinstance(au['subject-areas']['subject-area'], list):
                            au_area.extend(
                                [
                                    {
                                        'author_id': str(author_id),
                                        'code': x['code'],
                                        'abbrev': x['abbrev'],
                                        'subject_area': x['$']
                                    }
                                    for x in au['subject-areas']['subject-area']
                                ]
                            )
                    else:
                        au_area.append(
                            {
                                'author_id': '', 'code': '',
                                'abbrev': '', 'subject_area': ''
                            }
                        )
                    logger.debug(
                        'fetch_author_info: loop author_subject subject: {0}'.format(
                            au_area[0]['subject_area']
                        )
                    )
                    au_info['author'].append(au_core)
                    au_info['affiliation'].extend(au_affiliation)
                    au_info['subject_area'].extend(au_area)
                    logger.info(
                        '共有作者 {0} 获取作者 {1}: [{2}] '.format(
                            total_number,
                            i,
                            au_core['author_id'],
                            ', '.join([au_core['surname'], au_core['givenname']])
                        )
                    )
                    i += 1
                except QuotaExceeded as e:
                    api_key_i += 1
                    if api_key_i == len(api_keys):
                        ex = ' '.join(['fetch_author_info:', e])
                        logger.exception(ex)
                        raise NoAvailableKeys('Usable key exhausted.')

    except (ConnectionError, NewConnectionError, MaxRetryError) as e:
        # if the network has problem, record the id of author and affiliation
        error = ' '.join(
            [
                'fetch_document_info:',
                time.strftime('%Y-%m-%d %H:%M'), e,
                '{0} / {1}: [author_id: {2}] '.format(i, total_number, author_id)
            ]
        )
        logger.error(error)
    finally:
        result = dict()
        result['author'] = pd.DataFrame(au_info['author'])
        result['subject_area'] = pd.DataFrame(au_info['subject_area'])
        result['affiliation'] = pd.DataFrame(au_info['affiliation'])
        return result


# ------------------


def fetch_document_info(scopus_ids, api_keys):
    if not (hasattr(scopus_ids, '__getitem__') and hasattr(scopus_ids, '__iter__')):
        raise ValueError('affiliation_ids should be list-like object.')
    if not (hasattr(api_keys, '__getitem__') and hasattr(api_keys, '__iter__')):
        raise ValueError('api_keys should be list-like object.')
    doc_info = dict()
    doc_info['document'] = list()
    doc_info['author'] = list()
    doc_info['subject_area'] = list()
    doc_info['affiliation'] = list()
    doc_info['author_affiliation'] = list()
    doc_info['keyword'] = list()
    scopus_id = 'none'
    i = 1
    total_number = len(scopus_ids)
    try:
        api_key_i = 0
        for scopus_id in scopus_ids:
            quota_while = True
            while quota_while:
                try:
                    doc = get_document_info(scopus_id, api_keys[api_key_i])
                    quota_while = False
                    doc_core = dict()
                    doc_core['scopus_id'] = doc['coredata']['dc:identifier'] if 'dc:identifier' in doc[
                        'coredata'
                    ] else ''
                    doc_core['eid'] = doc['coredata']['eid'] if 'eid' in doc['coredata'] else ''
                    doc_core['pubmed_id'] = doc['coredata']['pubmed-id'] if 'pubmed-id' in doc['coredata'] else ''
                    doc_core['pii'] = doc['coredata']['pii'] if 'pii' in doc['coredata'] else ''
                    doc_core['doi'] = doc['coredata']['prism:doi'] if 'prism:doi' in doc['coredata'] else ''
                    doc_core['title'] = doc['coredata']['dc:title'] if 'dc:title' in doc['coredata'] else ''
                    logger.debug(' '.join(['获取文献：', doc_core['scopus_id']]))
                    doc_core['aggregation_type'] = doc['coredata'][
                        'prism:aggregationType'
                    ] if 'prism:aggregationType' in doc['coredata'] else ''
                    doc_core['srctype'] = doc['coredata']['srctype'] if 'srctype' in doc['coredata'] else ''
                    doc_core['citedby_count'] = doc['coredata']['citedby-count'] if 'citedby-count' in doc[
                        'coredata'
                    ] else ''
                    doc_core['publication_name'] = doc['coredata'][
                        'prism:publicationName'
                    ] if 'prism:publicationName' in doc['coredata'] else ''
                    doc_core['source_id'] = doc['coredata']['source-id'] if 'source-id' in doc['coredata'] else ''
                    doc_core['issn'] = doc['coredata']['prism:issn'] if 'prism:issn' in doc['coredata'] else ''
                    doc_core['volumn'] = doc['coredata']['prism:volume'] if 'prism:volume' in doc['coredata'] else ''
                    doc_core['issue_identifier'] = doc['coredata'][
                        'prism:issureIdentifier'
                    ] if 'prism:issureIdentifier' in doc['coredata'] else ''
                    doc_core['start_page'] = doc['coredata']['prism:startingPage'] if 'prism:startingPage' in doc[
                        'coredata'
                    ] else ''
                    doc_core['end_page'] = doc['coredata']['prism:endingPage'] if 'prism:endingPage' in doc[
                        'coredata'
                    ] else ''
                    doc_core['page_range'] = doc['coredata']['prism:pageRange'] if 'prism:pageRange' in doc[
                        'coredata'
                    ] else ''
                    doc_core['cover_date'] = doc['coredata']['prism:coverDate'] if 'prism:coverDate' in doc[
                        'coredata'
                    ] else ''
                    # affiliation information of document
                    doc_affiliation = list()
                    if 'affiliation' in doc:
                        if isinstance(doc['affiliation'], dict):
                            doc_affiliation.append(
                                {
                                    'scopus_id': str(scopus_id),
                                    'affiliation_id': doc['affiliation']['@id'],
                                    'affiliation_name': doc['affiliation']['affilname'],
                                    'affiliation_city': doc['affiliation']['affiliation-city'],
                                    'affiliation_country': doc['affiliation']['affiliation-country']
                                }
                            )
                        elif isinstance(doc['affiliation'], list):
                            doc_affiliation.extend(
                                [
                                    {
                                        'scopus_id': str(scopus_id),
                                        'affiliation_id': x['@id'],
                                        'affiliation_name': x['affilname'],
                                        'affiliation_city': x['affiliation-city'],
                                        'affiliation_country': x['affiliation-country']
                                    } for x in doc['affiliation']
                                ]
                            )
                    else:
                        doc_affiliation.append(
                            {
                                'scopus_id': '', 'affiliation_id': '', 'affiliation_name': '',
                                'affiliation_city': '', 'affiliation_country': ''
                            }
                        )
                    logger.debug(
                        'fetch_document_info: loop doc_affiliation affiliation_id: {0}'.format(
                            doc_affiliation[0]['affiliation_id']
                        )
                    )
                    # author information of document
                    doc_author = list()
                    if 'authors' in doc:
                        if isinstance(doc['authors']['author'], dict):
                            doc_author.append(
                                {
                                    'scopus_id': str(scopus_id),
                                    'author_id': doc['authors']['author']['@auid'],
                                    'idxname': doc['authors']['author']['ce:indexed-name'],
                                    'initialname': doc['authors']['author']['ce:initials'],
                                    'surname': doc['authors']['author']['ce:surname'],
                                    'rank': doc['authors']['author']['@seq']
                                }
                            )
                        elif isinstance(doc['authors']['author'], list):
                            doc_author.extend(
                                [
                                    {
                                        'scopus_id': scopus_id,
                                        'author_id': x['@auid'],
                                        'idxname': x['ce:indexed-name'],
                                        'initialname': x['ce:initials'],
                                        'surname': x['ce:surname'],
                                        'rank': x['@seq']
                                    }
                                    for x in doc['authors']['author']
                                ]
                            )
                    else:
                        doc_author.append(
                            {
                                'scopus_id': '', 'author_id': '', 'idxname': '',
                                'initialname': '', 'surname': '', 'rank': ''
                            }
                        )
                    logger.debug(
                        'fetch_document_info: loop doc_affiliation author_id: {0}'.format(
                            doc_author[0]['author_id']
                        )
                    )
                    doc_author_affiliation = list()
                    if 'authors' in doc:
                        if not isinstance(doc['authors']['author'], list):
                            doc['authors']['author'] = [doc['authors']['author']]
                        for au in doc['authors']['author']:
                            if isinstance(au['affiliation'], list):
                                doc_author_affiliation.extend(
                                    [
                                        {
                                            'scopus_id': str(scopus_id),
                                            'author_id': au['@auid'],
                                            'affiliation_id': x['@id']
                                        } for x in au['affiliation']
                                    ]
                                )
                            elif isinstance(au['affiliation'], dict):
                                doc_author_affiliation.append(
                                    {
                                        'scopus_id': str(scopus_id),
                                        'author_id': au['@auid'],
                                        'affiliation_id': au['affiliation']['@id']
                                    }
                                )
                    else:
                        doc_author_affiliation.append({'scopus_id': '', 'affiliation_id': ''})
                    logger.debug(
                        'fetch_document_info: loop doc_author_affiliation author_id: {0}, affiliation_id: {1}'.format(
                            doc_author_affiliation[0]['author_id'], doc_author_affiliation[0]['affiliation_id']
                        )
                    )
                    # subject information of document
                    doc_subject_area = list()
                    if 'subject-areas' in doc:
                        if isinstance(doc['subject-areas']['subject-area'], dict):
                            doc_subject_area.append(
                                {
                                    'scopus_id': str(scopus_id),
                                    'code': doc['subject-areas']['subject-area']['@code'],
                                    'abbrev': doc['subject-areas']['subject-area']['@abbrev'],
                                    'description': doc['subject-areas']['subject-area']['$']
                                }
                            )
                        elif isinstance(doc['subject-areas']['subject-area'], list):
                            doc_subject_area.extend(
                                [
                                    {
                                        'scopus_id': str(scopus_id),
                                        'code': x['@code'],
                                        'abbrev': x['@abbrev'],
                                        'description': x['$']
                                    }
                                    for x in doc['subject-areas']['subject-area']
                                ]
                            )
                    else:
                        doc_subject_area.append(
                            {'scopus_id': '', 'code': '', 'abbrev': '', 'description': ''}
                        )
                    logger.debug(
                        'fetch_document_info: loop subject_areas description: {0}'.format(
                            doc_subject_area[0]['description']
                        )
                    )
                    # keyword of document
                    doc_keyword = list()
                    if 'authkeywords' in doc:
                        if isinstance(doc['authkeywords']['author-keyword'], dict):
                            doc_keyword.append(
                                {
                                    'scopus_id': str(scopus_id),
                                    'keyword': doc['authkeywords']['author-keyword']['$']
                                }
                            )
                        elif isinstance(doc['authkeywords']['author-keyword'], list):
                            doc_keyword.extend(
                                [
                                    {
                                        'scopus_id': str(scopus_id),
                                        'keyword': x['$']
                                    }
                                    for x in doc['authkeywords']['author-keyword']
                                ]
                            )
                    else:
                        doc_keyword.append({'scopus_id': '', 'keyword': ''})
                    logger.debug('fetch_document_info: loop keyword: {0}'.format(doc_keyword[0]['keyword']))
                    doc_info['document'].append(doc_core)
                    doc_info['affiliation'].extend(doc_affiliation)
                    doc_info['author'].extend(doc_author)
                    doc_info['author_affiliation'].extend(doc_author_affiliation)
                    doc_info['subject_area'].extend(doc_subject_area)
                    doc_info['keyword'].extend(doc_keyword)
                    logger.info(
                        '共有文献 {0} 获取文献 {1} : [{2}] {3} '.format(
                            total_number,
                            i,
                            scopus_id,
                            doc_core['title']
                        )
                    )
                    i += 1
                except QuotaExceeded as e:
                    api_key_i += 1
                    if api_key_i == len(api_keys):
                        ex = ' '.join(['fetch_document_info:', e])
                        logger.exception(ex)
                        raise NoAvailableKeys('Usable key exhausted.')

    except (ConnectionError, NewConnectionError, MaxRetryError) as e:
        # if the network has problem, record the id of author and affiliation
        error = ' '.join(
            [
                'fetch_document_info:',
                time.strftime('%Y-%m-%d %H:%M'), e,
                '{0} / {1}: [scopus_id: {2}] '.format(i, len(scopus_ids), scopus_id)
            ]
        )
        logger.error(error)
    finally:
        result = dict()
        result['document'] = pd.DataFrame(doc_info['document'])
        result['author'] = pd.DataFrame(doc_info['author'])
        result['affiliation'] = pd.DataFrame(doc_info['affiliation'])
        result['author_affiliation'] = pd.DataFrame(doc_info['author_affiliation'])
        result['subject_area'] = pd.DataFrame(doc_info['subject_area'])
        result['keyword'] = pd.DataFrame(doc_info['keyword'])
        return result

# ------------------


def fetch_doc(affiliation_ids, author_ids, pubyear, yeardirection, api_keys):
    # input variables validation
    if not (hasattr(affiliation_ids, '__getitem__') and hasattr(affiliation_ids, '__iter__')):
        raise ValueError('affiliation_ids should be list-like object.')
    if not (hasattr(author_ids, '__getitem__') and hasattr(author_ids, '__iter__')):
        raise ValueError('author_ids should be list-like object.')
    if not (hasattr(api_keys, '__getitem__') and hasattr(api_keys, '__iter__')):
        raise ValueError('api_keys should be list-like object.')
    if len(affiliation_ids) != len(author_ids):
        raise UnmatchedLengthError('The length of affiliation_ids and author_ids should be the same.')
    if yeardirection not in ['>', '=', '<']:
        raise ValueError('yeardirection should be in >, =, <')
    # make store list
    author_doc = list()  # author_id, scopus_id
    document = list()  # scopus_id, title, eid, dc:creator, citedby_count
    doc_affiliation = list()  # scopus_id, affiliation_name, affiliation_city, affiliation_country
    api_key_i = 0
    pub_year_search = make_query_pubyear(pubyear, yeardirection)
    affiliation_id = 'none'
    author_id = 'none'
    i = 1
    total_number = len(author_ids)
    try:
        for author_id, affiliation_id in zip(author_ids, affiliation_ids):
            logger.info(
                '共有 {0} 获取 {1} : [作者 ID {2}, 单位 ID {3}] '.format(
                    total_number,
                    i,
                    author_id,
                    affiliation_id
                )
            )
            start = 0
            query_seq = '+'.join(
                [
                    make_query_author_id(author_id),
                    make_query_affiliation_id(affiliation_id),
                    pub_year_search
                ]
            )
            while_loop = True
            while while_loop:
                quota_while = True
                # api_key quota check
                while quota_while:
                    try:
                        # fetch document information
                        # scopus search,         20000
                        doc_info = search_document(
                            query_seq,
                            start, 200, api_keys[api_key_i]
                        )
                        quota_while = False
                    except QuotaExceeded as e:
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
                            ex = ' '.join(['fetch_document_info:', e])
                            logger.exception(ex)
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
                if start > total_count:
                    while_loop = False
            i += 1  # calculate the process ith of all
    except (ConnectionError, NewConnectionError, MaxRetryError) as e:
        # if the network has problem, record the id of author and affiliation
        error = ' '.join(
            [
                'fetch_document_info:',
                time.strftime('%Y-%m-%d %H:%M'), e,
                'Affiliation {0} Author {1} stopped.\n'.format(affiliation_id, author_id)
            ]
        )
        logger.error(error)
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

# ------------------
# EOF
# ------------------
