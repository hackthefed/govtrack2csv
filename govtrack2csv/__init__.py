# This file is part of govtrack2csv.
#
# Foobar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>

import json
import logging
import multiprocessing
import os
import os.path
import pandas as pd
import sys
import yaml  # Ruby users should die.

from govtrack2csv.util import datestring_to_datetime
from govtrack2csv.model import Congress
logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.DEBUG)


def import_legislators(src):
    """
    Read the legislators from the csv files into a single Dataframe. Intended for importing new data.
    """
    current = pd.DataFrame().from_csv("{0}/congress-legislators/legislators-current.csv".format(src))
    historic = pd.DataFrame().from_csv("{0}/congress-legislators/legislators-historic.csv".format(src))
    legislators = current.append(historic)

    # more than one thing has a thomas_id so it's kinda usless in our model
    legislators['legislator_id'] = legislators['thomas_id']

    return legislators


def save_legislators(legislators, destination):
    """
    Output legislators datafrom to csv.
    """
    legislators.to_csv("{0}/csv/legislators.csv".format(destination), encoding='utf-8')


#
# Committee Functions
#

def import_committees(src):
    """
    Read the committees from the csv files into a single Dataframe. Intended for importing new data.
    """
    committees = []
    subcommittees = []

    with open("{0}/congress-legislators/committees-current.yaml".format(src), 'r') as stream:
        committees += yaml.load(stream)

    with open("{0}/congress-legislators/committees-current.yaml".format(src), 'r') as stream:
        committees += yaml.load(stream)

    # Sub Committees are not Committees
    # And unfortunately the good folk at thomas thought modeling data with duplicate id's was a good idea.
    # you can have two subcommittees with the ID 12. Makes a simple membership map impossible.
    for com in committees:

        com['committee_id'] = com['thomas_id']

        if 'subcommittees' in com:
            # process sub committees into separate DataFrame
            for subcom in com.get('subcommittees'):
                subcom['committee_id'] = com['thomas_id']  # we use committee_id so we can easily merge dataframes
                subcom['subcommittee_id'] = "{0}-{1}".format(subcom['committee_id'], subcom['thomas_id'])
                subcommittees.append(subcom)

            del com['subcommittees']

    committees_df = pd.DataFrame(committees)
    subcommittees_df = pd.DataFrame(subcommittees)

    return [committees_df, subcommittees_df]


def save_committees(committees, dest):
    """
    Output legislators datafrom to csv.
    """
    committees.to_csv("{0}/csv/committees.csv".format(dest), encoding='utf-8')


def save_subcommittees(subcommittees, dest):
    """
    Output legislators datafrom to csv.
    """
    subcommittees.to_csv("{0}/csv/subcommittees.csv".format(dest), encoding='utf-8')


def make_congress_dir(congress, dest):
    """
    If the directory for a given congress does not exist. Make it.
    """

    congress_dir = "{0}/{1}".format(dest, congress)
    path = os.path.dirname(congress_dir)
    logger.debug("CSV DIR: {}".format(path))
    if not os.path.exists(congress_dir):
        logger.info("Created: {0}".format(congress_dir))
        os.mkdir(congress_dir)
    return congress_dir


def load_subjects(congresses):
    temp_array = []
    for con in congresses:
        t_con = pd.DataFrame().from_csv("data/csv/{0}/legislation.csv".format(con))
        temp_array.append(t_con)
    return pd.concat(temp_array)


def save_congress(congress, dest):
    """
    Takes a congress object with legislation, sponser, cosponsor, commities
    and subjects attributes and saves each item to it's own csv file.
    """
    try:
        logger.debug(congress.name)
        logger.debug(dest)
        congress_dir = make_congress_dir(congress.name, dest)
        logger.debug(congress_dir)
        congress.legislation.to_csv("{0}/legislation.csv".format(congress_dir), encoding='utf-8')
        congress.sponsors.to_csv("{0}/sponsor_map.csv".format(congress_dir), encoding='utf-8')
        congress.cosponsors.to_csv("{0}/cosponsor_map.csv".format(congress_dir), encoding='utf-8')
        # congress.events.to_csv("{0}/events.csv".format(congress_dir), encoding='utf-8')
        congress.committees.to_csv("{0}/committees_map.csv".format(congress_dir), encoding='utf-8')
        congress.subjects.to_csv("{0}/subjects_map.csv".format(congress_dir), encoding='utf-8')
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(exc_type, fname, exc_tb.tb_lineno)


def import_committee_membership(src):
    with open("{0}/congress-legislators/committee-membership-current.yaml".format(src), 'r') as stream:
        c_membership = yaml.load(stream)

    members = []

    for c in c_membership:
        for member in c_membership[c]:
            member['committee_id'] = c
            member['title'] = member.get('title', 'Member')
            member['party_position'] = member['party']
            member['legislator_id'] = int(member['thomas'])
            del(member['party'])
            del(member['thomas'])
            members.append(member)

    return pd.DataFrame(members)


def save_committee_membership(membership, dest):
    membership.to_csv("{0}/csv/membership.csv".format(dest), encoding='utf-8')


def extract_legislation(bill):
    """
    Returns a list of the legislation fields we need for our legislation DataFrame
    :param bill:
    :return list:
    """
    record = []
    record.append(bill.get('congress', None))
    record.append(bill.get('bill_id', None))
    record.append(bill.get('bill_type', None))
    record.append(bill.get('introduced_at', None))
    record.append(bill.get('number', None))
    record.append(bill.get('official_title', None))
    record.append(bill.get('popular_title', None))
    record.append(bill.get('short_title', None))
    record.append(bill.get('status', None))
    record.append(bill.get('status_at', None))
    record.append(bill.get('top_subject', None))
    record.append(bill.get('updated_at', None))

    return record


def extract_sponsor(bill):
    """
    Return a list of the fields we need to map a sponser to a bill
    """
    logger.debug("Extracting Sponsor")
    sponsor_map = []
    sponsor = bill.get('sponsor', None)
    if sponsor:
        sponsor_map.append(sponsor.get('type'))
        sponsor_map.append(sponsor.get('thomas_id'))
        sponsor_map.append(bill.get('bill_id'))
        sponsor_map.append(sponsor.get('district'))
        sponsor_map.append(sponsor.get('state'))
    logger.debug("END Extracting Sponsor")
    return sponsor_map


def extract_cosponsors(bill):
    """
    Return a list of list relating cosponsors to legislation.
    """
    logger.debug("Extracting Cosponsors")
    cosponsor_map = []
    cosponsors = bill.get('cosponsors', [])
    bill_id = bill.get('bill_id', None)

    for co in cosponsors:
        co_list = []
        co_list.append(co.get('thomas_id'))
        co_list.append(bill_id)
        co_list.append(co.get('district'))
        co_list.append(co.get('state'))
        cosponsor_map.append(co_list)

    logger.debug("End Extractioning Cosponsors")

    return cosponsor_map


def extract_subjects(bill):
    """
    Return a list subject for legislation.
    """
    logger.debug("Extracting Subjects")
    subject_map = []
    subjects = bill.get('subjects', [])
    bill_id = bill.get('bill_id', None)
    bill_type = bill.get('bill_type', None)

    for sub in subjects:
        subject_map.append((bill_id, bill_type, sub))

    logger.debug("End Extractioning Subjects")

    return subject_map


def extract_committees(bill):
    """
    Returns committee associations from a bill.
    """
    bill_id = bill.get('bill_id', None)
    logger.debug("Extracting Committees for {0}".format(bill_id))

    committees = bill.get('committees', None)
    committee_map = []

    for c in committees:
        logger.debug("Processing committee {0}".format(c.get('committee_id')))
        c_list = []
        sub = c.get('subcommittee_id')
        if sub:
            logger.debug("is subcommittee")
            c_list.append('subcommittee')  # type
            c_list.append(c.get('subcommittee'))
            sub_id = "{0}-{1}".format(c.get('committee_id'), c.get('subcommittee_id'))
            logger.debug("Processing subcommittee {0}".format(sub_id))
            c_list.append(sub_id)
        else:
            c_list.append('committee')
            c_list.append(c.get('committee'))
            c_list.append(c.get('committee_id'))
        c_list.append(bill_id)
        committee_map.append(c_list)
    return committee_map


# Really don't like how this is comming together.....
def extract_events(bill):
    """
    Returns all events  from legislations. Thing of this as a log for congress.
    There are alot of events that occur around legislation. For now we are
    going to kepe it simple. Introduction, cosponsor, votes dates
    """
    events = []
    logger.debug(events)

    bill_id = bill.get('bill_id', None)
    if bill_id:
        logger.debug('got bill id')
        intro_date = datestring_to_datetime(bill.get('introduced_at', None))
        sponsor = bill.get('sponsor', None)
        type = sponsor.get('type', None)
        id = bill.get('thomas_id', None)
        events.append((bill_id, 'introduced', type, id, intro_date))

    logger.debug(events)

    return events


def convert_congress(congress):
    """
    Recurse the passed govtrack congress directory and convert it's contents
    to a set of csv files from the legislation contained therein.
    :return dict: A Dictionary of DataFrames
    """

    logger.info("Begin processing {0}".format(congress))

    congress_obj = Congress(congress)

    logger.debug("made congress object")
    logger.debug(congress_obj)

    # We construct lists that can be used to construct dataframes.  Adding to
    # dataframes is expensive so we don't do  that.

    # Core Data
    legislation = []

    # Relationships
    # bills_per_congress = []
    sponsors = []
    cosponsors = []
    committees = []
    # ammendments = []
    subjects = []
    # titles = []
    # events = []

    # Change Log
    # actions = pd.DataFrame()

    bills = "{0}/{1}/bills".format(congress['src'], congress['congress'])
    logger.info("About to walk {0}".format(bills))

    for root, dirs, files in os.walk(bills):
        if "data.json" in files and "text-versions" not in root:
            file_path = "{0}/data.json".format(root)
            logger.debug("Processing {0}".format(file_path))
            bill = json.loads(open(file_path, 'r').read())

            logger.debug("OPENED {}".format(file_path))

            # let's start with just the legislative information
            try:
                record = extract_legislation(bill)
                legislation.append(record)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error(exc_type, fname, exc_tb.tb_lineno)

            try:
                sponsor = extract_sponsor(bill)
                sponsors.append(sponsor)
                logger.debug("sponsor")
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error(exc_type, fname, exc_tb.tb_lineno)

            try:
                cosponsor = extract_cosponsors(bill)
                cosponsors.extend(cosponsor)
                logger.debug("co-sponsor")
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error(exc_type, fname, exc_tb.tb_lineno)

            try:
                subject = extract_subjects(bill)
                subjects.extend(subject)

                committee = extract_committees(bill)
                committees.extend(committee)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error(exc_type, fname, exc_tb.tb_lineno)

    try:

        logger.debug(" ======================  SAVING {}".format(congress))

        congress_obj.legislation = pd.DataFrame(legislation)
        congress_obj.legislation.columns = [
            'congress', 'bill_id', 'bill_type', 'introduced_at', 'number',
            'official_title', 'popular_title', 'short_title', 'status', 'status_at',
            'top_subject', 'updated_at']

        congress_obj.sponsors = pd.DataFrame(sponsors)
        congress_obj.sponsors.columns = [
            'type', 'thomas_id', 'bill_id', 'district', 'state']

        congress_obj.cosponsors = pd.DataFrame(cosponsors)
        congress_obj.sponsors.columns = [
            'type', 'thomas_id', 'bill_id', 'district', 'state']

        congress_obj.committees = pd.DataFrame(committees)
        congress_obj.committees.columns = [
            'type', 'name', 'committee_id', 'bill_id']

        congress_obj.subjects = pd.DataFrame(subjects)
        congress_obj.subjects.columns = [
            'bill_id', 'bill_type', 'subject']

        # congress_obj.events = pd.DataFrame(events)
        save_congress(congress_obj, congress['dest'])
        # print "{0} - {1}".format(congress, len(legislation))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.debug(e)
        logger.debug(exc_type)
        logger.debug(fname)
        logger.debug(exc_tb.tb_lineno)
