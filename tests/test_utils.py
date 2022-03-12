import utils


def test_get_limits_api() -> None:
    url, auth = utils.limits_api()
    assert "execute-api" in url
    assert "execute-api" == auth.service


def test_get_accounts_api() -> None:
    url, auth = utils.accounts_api()
    assert "appsync-api" in url
    assert "appsync" == auth.service
