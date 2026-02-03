from ciam.auth import TokenManager, PINGONE_TOKEN_URLS


def test_prepare_requests_structure():
    tm = TokenManager()
    region, env = "us", "dev"
    token_url = PINGONE_TOKEN_URLS.get((region, env))
    assert token_url is not None, "Test token URL must exist in mapping"

    # Prepare general request
    general = tm.prepare_general_request("cid", "csecret", token_url)
    assert "headers" in general and "data" in general and "url" in general
    assert "Authorization" in general["headers"]
    assert general["data"].get("grant_type") == "client_credentials"

    # Prepare clientops request
    clientops = tm.prepare_clientops_request("cid2", "csecret2", token_url)
    assert "Authorization" not in clientops["headers"]
    assert clientops["data"].get("client_id") == "cid2"
    assert clientops["data"].get("client_secret") == "csecret2"


if __name__ == "__main__":
    test_prepare_requests_structure()
    print("Auth request preparation smoke checks passed.")
