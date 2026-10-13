import httpx, json, os, sys

BASE = 'http://localhost:8000'

def register(email):
    payload = {
        'name': 'Test User',
        'email': email,
        'password': 'test1234',
        'dosage_frequency': 2,
        # omit treatment_start_date to use default
    }
    r = httpx.post(f'{BASE}/auth/register', json=payload)
    print('REGISTER status', r.status_code)
    print('Response:', r.text)
    if r.status_code != 200:
        sys.exit(1)
    return r.json()['access_token']

def login(email):
    payload = {'email': email, 'password': 'test1234'}
    r = httpx.post(f'{BASE}/auth/login', json=payload)
    print('LOGIN status', r.status_code)
    print('Response:', r.text)
    if r.status_code != 200:
        sys.exit(1)
    return r.json()['access_token']

def get_dashboard(token):
    # Simple health check
    r = httpx.get(f'{BASE}/')
    print('Root fetch status', r.status_code)
    print('Root content snippet:', r.text[:100])

if __name__ == '__main__':
    test_email = f'test_{int(os.urandom(2).hex(),16)}@example.com'
    token = register(test_email)
    token2 = login(test_email)
    # Tokens may differ per request; just ensure both are non-empty
    if not token or not token2:
        raise RuntimeError('Failed to obtain tokens')
    print('Tokens obtained successfully')
    get_dashboard(token)
    get_dashboard(token)
