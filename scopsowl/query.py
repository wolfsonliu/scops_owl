# ------------------
# Import Libraries
# ------------------
import requests
import logging

# ------------------


# ------------------
# Errors and logs
# ------------------
logger = logging.getLogger('scops_owl.query')


class InvalidInput(ValueError):
    pass


class QuotaExceeded(ValueError):
    pass


# ------------------
# Functions
# ------------------
def get_affiliation_info(affiliation_id, api_key):
    # get affiliation request
    # affiliation retrieval quota per week 5000
    affiliation_id = str(affiliation_id)
    api_key = str(api_key)
    affiliation_url = requests.get(
        ''.join(
            [
                'http://api.elsevier.com/content/affiliation/affiliation_id/',
                affiliation_id,
                '?apiKey=',
                api_key,
                '&httpAccept=application%2Fjson'
            ]
        )
    )
    logger.debug('get_affiliation_info(): request url: {0}'.format(affiliation_url.url))
    if 'service-error' in affiliation_url.json():
        if affiliation_url.json()['service-error']['status']['statusCode'] == 'INVALID_INPUT':
            raise InvalidInput(
                ': '.join(
                    ['affiliation_id', affiliation_id, affiliation_url.json()['service-error']['status']['statusText']]
                )
            )
        elif affiliation_url.json()['service-error']['status']['statusCode'] == 'QUOTA_EXCEEDED':
            raise QuotaExceeded(
                ': '.join(
                    ['affiliation_id', affiliation_id, affiliation_url.json()['service-error']['status']['statusText']]
                )
            )
    else:
        # parse xml file to dict
        affiliation_json = affiliation_url.json()['affiliation-retrieval-response']
        parsed_dict = dict()
        parsed_dict['coredata'] = affiliation_json['coredata']
        parsed_dict['affiliation-name'] = affiliation_json[
            'affiliation-name'
        ] if 'affiliation-name' in affiliation_json else ''
        parsed_dict['address'] = affiliation_json['address'] if 'address' in affiliation_json else ''
        parsed_dict['city'] = affiliation_json['city'] if 'city' in affiliation_json else ''
        parsed_dict['country'] = affiliation_json['country'] if 'country' in affiliation_json else ''
        parsed_dict['profile'] = affiliation_json['institution-profile']
        return parsed_dict


# ------------------
def get_document_info(scopus_id, api_key):
    # get document request
    # abstract retrieval quota per week 10000
    scopus_id = str(scopus_id)
    api_key = str(api_key)
    doc_url = requests.get(
        ''.join(
            [
                'http://api.elsevier.com/content/abstract/scopus_id/',
                scopus_id,
                '?apiKey=',
                api_key,
                '&httpAccept=application%2Fjson'
            ]
        )
    )
    logger.debug('get_document_info: request url: {0}'.format(doc_url.url))
    if 'service-error' in doc_url.json():
        if doc_url.json()['service-error']['status']['statusCode'] == 'INVALID_INPUT':
            raise InvalidInput(
                ': '.join(
                    ['scopus_id', scopus_id, doc_url.json()['service-error']['status']['statusText']]
                )
            )
        elif doc_url.json()['service-error']['status']['statusCode'] == 'QUOTA_EXCEEDED':
            raise QuotaExceeded(
                ': '.join(
                    ['scopus_id', scopus_id, doc_url.json()['service-error']['status']['statusText']]
                )
            )
    else:
        doc_json = doc_url.json()['abstracts-retrieval-response']
        return doc_json


# ------------------
def get_author_info(author_id, api_key):
    # author retrieval quota per week 5000
    author_id = str(author_id)
    api_key = str(api_key)
    au_url = requests.get(
        ''.join(
            [
                'http://api.elsevier.com/content/author/author_id/',
                author_id,
                '?apiKey=',
                api_key,
                '&httpAccept=application%2Fjson'
            ]
        )
    )
    logger.debug('get_author_info: request url: {0}'.format(au_url.url))
    if 'service-error' in au_url.json():
        if au_url.json()['service-error']['status']['statusCode'] == 'INVALID_INPUT':
            raise InvalidInput(
                ': '.join(
                    ['author_id', author_id, au_url.json()['service-error']['status']['statusText']]
                )
            )
        elif au_url.json()['service-error']['status']['statusCode'] == 'QUOTA_EXCEEDED':
            raise QuotaExceeded(
                ': '.join(
                    ['author_id', author_id, au_url.json()['service-error']['status']['statusText']]
                )
            )
    else:
        au_json = au_url.json()['author-retrieval-response'][0]
        return au_json


# ------------------
def make_query_affiliation_id(affiliation_id):
    return 'af-id(' + str(affiliation_id) + ')'


# ------------------
def make_query_author_id(author_id):
    return 'au-id(' + str(author_id) + ')'


# ------------------
def make_query_pubyear(pubyear, yeardirection):
    if yeardirection not in ['>', '=', '<']:
        raise ValueError('yeardirection should be in >, =, <')
    return ' '.join(['pubyear', yeardirection, str(pubyear)])


# ------------------
def search_author(query, start, count, api_key):
    # author search quota per week 5000
    affau_url = requests.get(
        ''.join(
            [
                'http://api.elsevier.com/content/search/author',
                '?start=',
                str(start),
                '&count=',
                str(count),
                '&query=',
                query,
                '&apiKey=',
                api_key,
                '&httpAccept=application%2Fjson'
            ]
        )
    )
    affau_json = affau_url.json()
    if 'service-error' in affau_json:
        if affau_json['service-error']['status']['statusCode'] == 'INVALID_INPUT':
            raise InvalidInput(
                ': '.join(
                    ['query', query, affau_json['service-error']['status']['statusText']]
                )
            )
        elif affau_json['service-error']['status']['statusCode'] == 'QUOTA_EXCEEDED':
            raise QuotaExceeded(
                ': '.join(
                    ['query', query, affau_json['service-error']['status']['statusText']]
                )
            )
    else:
        result = dict()
        result['total_count'] = affau_json['search-results']['opensearch:totalResults']
        result['authors'] = affau_json['search-results']['entry']
        return result


# ------------------
def search_document(query, start, count, api_key):
    # scopus search quota per week 20000
    affdoc_url = requests.get(
        ''.join(
            [
                'http://api.elsevier.com/content/search/scopus',
                '?start=',
                str(start),
                '&count=',
                str(count),
                '&query=',
                query,
                '&apiKey=',
                api_key,
                '&httpAccept=application%2Fjson'
            ]
        )
    )
    affdoc_json = affdoc_url.json()
    if 'service-error' in affdoc_json:
        if affdoc_json['service-error']['status']['statusCode'] == 'INVALID_INPUT':
            raise InvalidInput(
                ': '.join(
                    ['query', query, affdoc_json['service-error']['status']['statusText']]
                )
            )
        elif affdoc_json['service-error']['status']['statusCode'] == 'QUOTA_EXCEEDED':
            raise QuotaExceeded(
                ': '.join(
                    ['query', query, affdoc_json['service-error']['status']['statusText']]
                )
            )
    else:
        result = dict()
        result['total_count'] = affdoc_json['search-results']['opensearch:totalResults']
        result['documents'] = affdoc_json['search-results']['entry']
        return result
# ------------------

# ------------------
# EOF
# ------------------
