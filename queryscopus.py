import requests

class InvalidInputError(ValueError):
    pass

class QuotaExceededError(ValueError):
    pass

def get_affiliation_info(affiliation_id, api_key):
    # get affiliation request
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

def get_document(scopus_id, api_key):
    # get document request
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
    doc_json = doc_url.json()['abstracts-retrieval-response']
    parsed_dict = dict()
    parsed_dict['document'] = dict()
    parsed_dict['document']['scopus_id'] = doc_json['coredata']['dc:identifier'] if 'dc:identifier' in doc_json['coredata'] else ''
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
    parsed_dict['author'] = doc_json['authors']['author']
    return parsed_dict

def get_author(authoer_id, api_key):
    au_url = requests.get(
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

def makequery_affiliation_id(affiliation_id):
    return 'af-id(' + str(affiliation_id) + ')'

def makequery_author_id(author_id):
    return 'au-id(' + str(author_id) + ')'

def search_author(query, start, count, api_key):
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
                ': '.join(['affiliation_id', affiliation_id] + affau_json['service-error']['status']['statusText'])
            )
        elif affau_json['service-error']['status']['statusCode'] == 'QUOTA_EXCEEDED':
            raise QuotaExceeded(
                ': '.join(['affiliation_id', affiliation_id] + affau_json['service-error']['status']['statusText'])
            )
    else:
        result = dict()
        result['total_count'] = affau_json['search-results']['opensearch:totalResults']
        result['authors'] = affau_json['search-results']['entry']
        return result

def search_document(query, start, count, api_key):
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
                ': '.join(['affiliation_id', affiliation_id] + affdoc_json['service-error']['status']['statusText'])
            )
        elif affdoc_json['service-error']['status']['statusCode'] == 'QUOTA_EXCEEDED':
            raise QuotaExceeded(
                ': '.join(['affiliation_id', affiliation_id] + affdoc_json['service-error']['status']['statusText'])
            )
    else:
        result = dict()
        result['total_count'] = affdoc_json['search-results']['opensearch:totalResults']
        result['documents'] = affdoc_json['search-results']['entry']
        return result



