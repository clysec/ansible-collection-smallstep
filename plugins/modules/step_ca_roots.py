#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: step_ca_roots
short_description: Get Root certificates from Step CA
version_added: "2.8"
description:
  - "Fetches the root certificates from Step CA."
options:
    ca_url:
        description:
          - URL of the Step CA server.
        required: true
        type: str
author:
    - Lars Scheibling (Cloudyne Systems)
'''

EXAMPLES = '''
# Pass in a custom name
- name: Get roots from Step CA
  step_ca_roots::
    ca_url: https://ca.example.com
'''

RETURN = '''
roots:
  description: Roots from Step CA
  type: List[str]
  sample: [
    "-----BEGIN CERTIFICATE-----\nMIID...==\n-----END CERTIFICATE-----",
    "-----BEGIN CERTIFICATE-----\nMIID...==\n-----END CERTIFICATE-----"
  ]
'''

import requests
import urllib.parse
import urllib3
from ansible.module_utils.basic import AnsibleModule


FACTS = []


def run_module():
    module_args = dict(
        ca_url=dict(type='str', default=''),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        roots=[]
    )

    full_url = urllib.parse.urljoin(
        module.params['ca_url'],
        'roots'
    )

    # Ignore SSL certificate verification
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Fetch the root certificates from Step CA
    resp = requests.get(
        str(full_url),
        headers={'Accept': 'application/x-pem-file'},
        verify=False,
    )

    if resp.status_code > 299:
        module.fail_json(
            msg='Failed to fetch roots from Step CA',
            status_code=resp.status_code,
            response=resp.text
        )
    else:
        parsed_roots = resp.json()
        if 'crts' in parsed_roots:
            result['roots'] = parsed_roots['crts']
        else:
            # Fallback to PEM format
            # Split the response text into individual certificates
            result['roots'] = resp.text.split('-----END CERTIFICATE-----')
            result['roots'] = [cert + '-----END CERTIFICATE-----' for cert in result['roots'] if cert.strip()]

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()