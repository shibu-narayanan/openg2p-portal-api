from openg2p_portal_api.config import Settings

_config = Settings.get_config()


def base_setup():
    _config.auth_default_issuers = ["http://localhost"]
    _config.auth_default_jwks_urls = ["http://localhost/.well-known/jwks.json"]
    _config.auth_id_types_ids = {"http://localhost": 3}
    _config.db_dbname = "testdb"

    # Initializer()

    # initialise controller, database, programsummary, get a dummy jwt

    # ProgramController()
