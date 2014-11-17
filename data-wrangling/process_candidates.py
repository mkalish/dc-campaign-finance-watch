#!user/bin/python
import csv
from candidate_record import get_or_create_candidate, save_candidate
from contribution_record import save_contribution
import data_util
path = '../csv/ocf_contributions.csv'

ocf_contributions_field_name = ['committee_name','candidate_name','contributor','address','city','state','zip','contributor_type','contribution_type','employer_name','employer_address','amount','date_of_receipt','office','election_year']


def process_candidates(): 
    rows = csv.DictReader(open(path), fieldnames=ocf_contributions_field_name)
    next(rows)
    for row in rows:
        candidate = get_or_create_candidate(row['candidate_name'], row['committee_name'])
        if row['contributor_type'] == 'Individual':
            candidate['individual_donor_count']+=1
        elif row['contributor_type'] == 'Corporation':
            candidate['corporate_donor_count']+=1
        else:
            candidate['other_donor_count']+=1

        __process_corporate_to_grass_root_ratio(candidate)
        __process_contribution_quality(candidate, row)
        __insert_contribution(candidate['_id'], candidate['committee_name'], row)
        save_candidate(candidate)


def __process_corporate_to_grass_root_ratio(candidate):
    if candidate['corporate_donor_count'] == 0:
        return 0
    elif candidate['individual_donor_count'] == 0:
        return 1
    else:
        return candidate['corporate_donor_count']/candidate['individual_donor_count']

def __process_contribution_quality(candidate, row):
    quality = 0
    if row['contributor'] and row['contributor'] != '':
        quality+=1
    if row['address'] and row['address'] != '':
        quality+=1
    if row['city'] and row['city'] != '':
        quality+=1
    if row['state'] and row['state'] != '':
        quality+=1
    if row['zip'] and row['zip'] != '':
        quality+=1
    if row['contributor_type'] == 'Individual' or row['contributor_type'] == 'Corporatation':
        quality+=1
    if row['amount'] and row['amount'] != '':
        quality+=1
    if row['date_of_receipt'] and data_util.extract_dates(row['date_of_receipt']) != '':
        quality+=1

    candidate['contributor_quality'] += quality


def __insert_contribution(candidate_name, committee, row):
    contribution = {}
    contribution['candidate'] = candidate_name
    contribution['candidate_committee'] = committee
    if data_util.extract_dates(row['date_of_receipt']) != '':
        contribution['date'] = data_util.extract_dates(row['date_of_receipt'])
    try:
        contribution['amount'] = float(row['amount'].replace('$',''))
    except:
        contribution['amount'] = float(0)

    contribution['type'] = row['contributor_type']
    contribution['contributor'] = row['contributor']
    address = {}
    address['line_one'] = row['address']
    address['city'] = row['city']
    address['zip'] = row['zip']
    address['state'] = row['state']
    contribution['address'] = address
    save_contribution(contribution)
