"""
This small utility parses all the FedRAMP moderate controls and displays the
compliance as code content rules that apply to those controls.
"""

import os
import logging
import tempfile

import git
import pandas as pd
import requests


FEDRAMP_SHEET = 'https://www.fedramp.gov/assets/resources/documents/FedRAMP_Security_Controls_Baseline.xlsx'
COMPLIANCE_CONTENT_REPO = 'https://github.com/ComplianceAsCode/content.git'


def get_fedramp_sheet(workspace):
    """ Get the FedRAMP controls excel sheet """
    logging.info("Fetching FedRAMP controls sheet from: %s", FEDRAMP_SHEET)
    fedramp_path = os.path.join(workspace, 'fedrampcontrols.xlsx')
    with open(fedramp_path, 'wb') as fedramp_file:
        fedramp_content = requests.get(FEDRAMP_SHEET).content
        fedramp_file.write(fedramp_content)
    return fedramp_path

def get_compliance_content(workspace):
    """ Clone the ComplianceAsCode content repository """
    logging.info("Fetching ComplianceAsCode content repository: %s",
                 COMPLIANCE_CONTENT_REPO)
    content_path = os.path.join(workspace, 'compliance-content')
    os.mkdir(content_path)
    git.Repo.clone_from(COMPLIANCE_CONTENT_REPO, content_path, branch='master')
    return content_path

def get_fedramp_moderate_controls(fedramp_path):
    """ Get a list of controls that apply to FedRAMP moderate """
    xlfile = pd.ExcelFile(fedramp_path)
    df1 = xlfile.parse('Moderate Baseline Controls')
    # The first line doesn't contain the right titles... e.g. "Unnamed: 3"
    # after getting the title, the next line contains the actual titles... so
    # we skip it. The rest should be the actual list of controls.
    return df1['Unnamed: 3'][1:]

def print_files_for_controls(fedramp_controls, content_path):
    """ Print the relevant files from the ComplianceAsCode project that are
    relevant to the NIST controls """
    for control in fedramp_controls:
        command = (("grep -R 'nist:' %s | grep '%s' |grep rule.yml | " +
                    "awk '{print $1}' | sed 's/:$//' | sed 's@^%s@@'") %
                   (content_path, control, content_path + '/'))
        stdout = os.popen(command)
        output = stdout.read()
        if output:
            print("The control '%s' is mentioned in the following rules:\n" %
                  control)
            print(output)

def main():
    """ read the fedramp controls! """
    with tempfile.TemporaryDirectory() as workspace:
        fedramp_path = get_fedramp_sheet(workspace)
        fedramp_controls = get_fedramp_moderate_controls(fedramp_path)
        content_path = get_compliance_content(workspace)
        print_files_for_controls(fedramp_controls, content_path)

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    main()