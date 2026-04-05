import re
import httpx

class GithubService:
    def __init__(self, token: str):
        self.token = token
        self.headers =  {
            'Authorization' : f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        self.base_url = 'https//api.github.com'
    
    def parse_url(self, pr_url:str) -> dict:
        regex_pattern = r'github\.com/([^/]+)/([^/]+)/pull/(\d+)'
        match = re.search(regex_pattern, pr_url)

        if not match:
            raise ValueError(f"URL de PR invalide : {pr_url}")
        
        return {
            'owner': match.group(1),
            'repo':  match.group(2),
            'number': int(match.group(3)),
        }

    def get_pr_diff(self, pr_url:str) -> dict:
        pr_info = self.parse_pr_url(pr_url)
        owner  = pr_info['owner']
        repo   = pr_info['repo']
        number = pr_info['number']

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{number}"

        with httpx.Client() as client:
            response = client.get(url,headers=self.headers)
            response.raise_for_status()
            pr_data = response.json()
        
            diff_headers = {
                **self.headers,
                'Accept': 'application/vnd.github.v3.diff',
            }
            diff_response = client.get(url, headers=diff_headers)
            diff_response.raise_for_status()
            diff_text = diff_response.text

            return {
            'owner':       owner,
            'repo':        repo,
            'number':      number,
            'repo_name':   f"{owner}/{repo}",
            'title':       pr_data.get('title', ''),
            'description': pr_data.get('body', ''),
            'diff':        diff_text,
            'files_count': pr_data.get('changed_files', 0),
        }

