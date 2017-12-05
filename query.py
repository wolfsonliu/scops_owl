# ------------------
# Import Libraries
# ------------------
import requests
# ------------------


# ------------------
# Errors
# ------------------
class InvalidInput(ValueError):
    pass


class QuotaExceeded(ValueError):
    pass
# ------------------


# ------------------
# Functions
# ------------------
def get_affiliation_info(affiliation_id, api_key):
    # get affiliation request
    # affiliation retrieval quota per week 5000
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
        parsed_dict['affiliation_name'] = affiliation_json['affiliation-name']
        parsed_dict['eid'] = affiliation_json['coredata']['eid']
        parsed_dict['author_count'] = affiliation_json['coredata']['author-count']
        parsed_dict['document_count'] = affiliation_json['coredata']['document-count']
        parsed_dict['affiliation_id'] = affiliation_json['coredata']['dc:identifier'].replace('AFFILIATION_ID:', '')
        parsed_dict['address_countryshort'] = affiliation_json['institution-profile']['address']['@country']
        parsed_dict['address_part'] = affiliation_json['institution-profile']['address']['address-part']
        parsed_dict['address_city'] = affiliation_json['institution-profile']['address']['city']
        parsed_dict['address_country'] = affiliation_json['institution-profile']['address']['country']
        parsed_dict['address_postalcode'] = affiliation_json['institution-profile']['address']['postal-code']
        parsed_dict['address_state'] = affiliation_json['institution-profile']['address']['state']
        parsed_dict['org_type'] = affiliation_json['institution-profile']['org-type']
        parsed_dict['org_domain'] = affiliation_json['institution-profile']['org-domain']
        parsed_dict['org_url'] = affiliation_json['institution-profile']['org-URL']
        return parsed_dict


# ------------------
def get_document(scopus_id, api_key):
    # get document request
    # abstract retrieval quota per week 10000
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
        parsed_dict = dict()
        parsed_dict['document'] = dict()
        parsed_dict['document']['scopus_id'] = doc_json[
            'coredata'
        ][
            'dc:identifier'
        ] if 'dc:identifier' in doc_json['coredata'] else ''
        parsed_dict['document']['eid'] = doc_json['coredata']['eid'] if 'eid' in doc_json['coredata'] else ''
        parsed_dict['document']['pubmed_id'] = doc_json['coredata']['pubmed-id']
        parsed_dict['document']['pii'] = doc_json['coredata']['pii']
        parsed_dict['document']['doi'] = doc_json['coredata']['prism:doi']
        parsed_dict['document']['title'] = doc_json['coredata']['dc:title']
        parsed_dict['document']['aggregation_type'] = doc_json['coredata']['prism:aggregationType']
        parsed_dict['document']['srctype'] = doc_json['coredata']['srctype']
        parsed_dict['document']['citedby_count'] = doc_json['coredata']['citedby-count']
        parsed_dict['document']['publication_name'] = doc_json['coredata']['prism:publicationName']
        parsed_dict['document']['source_id'] = doc_json['coredata']['source-id']
        parsed_dict['document']['issn'] = doc_json['coredata']['prism:issn']
        parsed_dict['document']['volumn'] = doc_json['coredata']['prism:volume']
        parsed_dict['document']['issue_identifier'] = doc_json['coredata']['prism:issureIdentifier']
        parsed_dict['document']['start_page'] = doc_json['coredata']['prism:startingPage']
        parsed_dict['document']['end_page'] = doc_json['coredata']['prism:endingPage']
        parsed_dict['document']['page_range'] = doc_json['coredata']['prism:pageRange']
        parsed_dict['document']['cover_date'] = doc_json['coredata']['prism:coverDate']
        parsed_dict['document']['affiliation_id'] = doc_json['affiliation']['@id']
        parsed_dict['document']['affiliation_name'] = doc_json['affiliation']['affilname']
        parsed_dict['document']['affiliation_city'] = doc_json['affiliation']['affiliation-city']
        parsed_dict['document']['affiliation_country'] = doc_json['affiliation']['affiliation-country']
        parsed_dict['subject_area'] = doc_json['subject-areas']['subject-area']
        parsed_dict['author'] = [
            {
                'author_id': x['@auid'], 'idxname': x['ce:indexed-name'], 'initialname': x['ce:initials'],
                'surname': x['ce:surname'], 'givenname': x['ce:given-name'], 'rank': x['@seq'],
                'affiliaion_id': x['affiliation']['@id']
            }
            for x in doc_json['authors']['author']
        ]
        return parsed_dict


# ------------------
def get_author(author_id, api_key):
    # author retrieval quota per week 5000
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
        parsed_dict = dict()
        parsed_dict['author'] = dict()
        parsed_dict['author']['author_id'] = au_json['coredata']['dc:identifier']
        parsed_dict['author']['eid'] = au_json['coredata']['eid']
        parsed_dict['author']['document_count'] = au_json['coredata']['document-count']
        parsed_dict['author']['cited_by_couunt'] = au_json['coredata']['cited-by-count']
        parsed_dict['author']['citation_count'] = au_json['coredata']['citation-count']
        parsed_dict['author']['affiliation_id'] = au_json['affiliation-current']['@id']
        parsed_dict['author']['surname'] = au_json['author-profile']['preferred-name']['surname']
        parsed_dict['author']['idxname'] = au_json['author-profile']['preferred-name']['indexed-name']
        parsed_dict['author']['initialname'] = au_json['author-profile']['preferred-name']['initials']
        parsed_dict['author']['givenname'] = au_json['author-profile']['preferred-name']['given-name']
        parsed_dict['affiliation'] = au_json['author-profile']['affiliation-history']['affiliation']
        parsed_dict['subject_area'] = au_json['subject-areas']['subject-area']
        return parsed_dict


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
