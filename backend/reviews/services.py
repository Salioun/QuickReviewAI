import re
import httpx
import anthropic
import json

class GithubService:
    def __init__(self, token: str):
        self.token = token
        self.headers =  {
            'Authorization' : f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        self.base_url = "https://api.github.com"
    
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
        pr_info = self.parse_url(pr_url)
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

class LLMService:
    MAX_TOKENS = 15000

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def _truncate_diff(self, diff: str) -> str:
        if len(diff) <= self.MAX_TOKENS:
            return diff
        truncated_diff = diff[:self.MAX_TOKENS]
        return f"{truncated_diff}\n...\n(diff tronqué pour respecter la limite de tokens)"
    
    def _build_prompt(self, pr_data: dict) -> str:
        diff = self._truncate_diff(pr_data['diff'])
        prompt = f"""
        Tu es un senior software engineer qui fait une code review professionnelle.
        Analyse ce Pull Request GitHub et retourne une review structurée.
        ## Informations du Pull Request
        - Repo : {pr_data['repo_name']}
        - Numéro : #{pr_data['number']}
        - Titre : {pr_data['title']}
        - Description : {pr_data.get('description') or 'Aucune description fournie'}
        - Fichiers modifiés : {pr_data['files_count']}
        ## Diff
        {diff}
        ## Instructions
        Réponds UNIQUEMENT avec un objet JSON valide, sans aucun autre texte avant ou après.
        La structure de l'objet JSON doit être exactement:
        {{
            "score": <entier entre 0 et 10>,
            "summary": "<résumé global de la review> en 2-3 phrases",
            "bugs": [
                {{
                "severity": "critical" | "major" | "minor",
                "file": "<nom du fichier>",
                "line": "<numéro de ligne approximatif ou null>",
                "description": "<description claire du bug>",
                "suggestion": "<comment le corriger>"
                }}
            ]
            "suggestions": [
                {{
                "category": "performance" | "readability" | "security" | "maintainability" | "testing",
                "file": "<nom du fichier ou 'global'>",
                "description": "<description de l'amélioration>",
                "suggestion": "<exemple concret si possible>"
                }}
            ],
            "performance": [
                {{
                "file": "<nom du fichier>",
                "description": "<problème de performance identifié>",
                "suggestion": "<optimisation proposée>"
                }}
            ],
            "positive_points": [
                "<ce qui est bien fait dans ce PR>"
            ]
        }}
        Règles :
        - Le score reflète la qualité globale (10 = parfait, 1 = dangereux en prod)
        - bugs peut être vide [] si aucun bug trouvé
        - Sois précis et actionnable — pas de commentaires vagues
        - Réponds en français"""

        return prompt

    def generate_review(self, pr_data: dict) -> dict:
        prompt = self._build_prompt(pr_data)
        response = self.client.messages.create(
            model="claude-haiku-4-5",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
        )

        raw_text = response.content[0].text
        cleaned_text = re.sub(r'^```json\s*', '', raw_text.strip())
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)


        try:
            review_data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"La réponse JSON n'est pas valide : {e}\n"
                f"Raw text: {raw_text[:500]}"
            )

        return review_data
