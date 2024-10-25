import xmlrpc.client

from openg2p_fastapi_common.errors.http_exceptions import BadRequestError

from openg2p_portal_api.exception import handle_exception

from ..config import Settings

_config = Settings.get_config()


def get_odoo_connection():
    """
    Connect to Odoo server and authenticate.
    """
    try:
        url = _config.odoo_url
        db = _config.odoo_db
        username = _config.odoo_username
        password = _config.odoo_password

        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise BadRequestError(
                "Authentication failed. Please check your credentials."
            )
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

        return models, db, uid, password
    except xmlrpc.client.Fault as e:
        handle_exception(e, f"XMLRPC Fault: {e.faultCode} - {e.faultString}")
    except Exception as e:
        handle_exception(e, f"Error connecting to Odoo: {str(e)}")
