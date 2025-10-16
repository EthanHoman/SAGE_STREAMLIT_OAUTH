"""
Authentication module for SAGE - NASA Launchpad OIDC Integration
"""

import streamlit as st
import requests
import logging
import jwt
from streamlit_oauth import OAuth2Component
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OIDCMetadata:
    """Class to fetch and store OIDC metadata from NASA Launchpad."""

    def __init__(self, issuer_url: str):
        self.issuer_url = issuer_url
        self.metadata = None
        self._fetch_metadata()

    def _fetch_metadata(self) -> None:
        """Fetch OIDC metadata from the well-known endpoint."""
        try:
            logger.info(f"Fetching OIDC metadata from: {self.issuer_url}")
            response = requests.get(self.issuer_url, timeout=10)
            response.raise_for_status()
            self.metadata = response.json()
            logger.info("OIDC metadata fetched successfully")
        except Exception as e:
            logger.error(f"Failed to fetch OIDC metadata: {str(e)}")
            raise Exception(f"Could not fetch OIDC metadata: {str(e)}")

    def get_authorization_endpoint(self) -> str:
        """Get the authorization endpoint URL."""
        return self.metadata.get("authorization_endpoint", "")

    def get_token_endpoint(self) -> str:
        """Get the token endpoint URL."""
        return self.metadata.get("token_endpoint", "")

    def get_userinfo_endpoint(self) -> str:
        """Get the userinfo endpoint URL."""
        return self.metadata.get("userinfo_endpoint", "")

    def get_end_session_endpoint(self) -> Optional[str]:
        """Get the end session (logout) endpoint URL."""
        return self.metadata.get("end_session_endpoint")

    def get_revocation_endpoint(self) -> Optional[str]:
        """Get the token revocation endpoint URL."""
        return self.metadata.get("revocation_endpoint")

    def get_issuer(self) -> str:
        """Get the issuer URL."""
        return self.metadata.get("issuer", "")


@st.cache_resource
def initialize_oauth_component() -> OAuth2Component:
    """
    Initialize and return the OAuth2Component with NASA Launchpad configuration.
    This is cached to avoid re-fetching metadata on every rerun.
    """
    try:
        # Get configuration from secrets
        client_id = st.secrets["oauth"]["client_id"]
        client_secret = st.secrets["oauth"]["client_secret"]
        issuer_url = st.secrets["oauth"]["issuer_url"]

        # Fetch OIDC metadata
        oidc_metadata = OIDCMetadata(issuer_url)

        # Get endpoints from metadata
        authorize_endpoint = oidc_metadata.get_authorization_endpoint()
        token_endpoint = oidc_metadata.get_token_endpoint()

        # NASA Launchpad ADFS may not provide these endpoints in metadata
        # Using token endpoint as placeholder for refresh/revoke (will need to verify with NASA docs)
        refresh_token_endpoint = token_endpoint
        revoke_token_endpoint = oidc_metadata.get_revocation_endpoint() or token_endpoint

        logger.info(f"Initializing OAuth2Component with endpoints:")
        logger.info(f"  Authorization: {authorize_endpoint}")
        logger.info(f"  Token: {token_endpoint}")

        # Initialize OAuth2Component
        oauth2 = OAuth2Component(
            client_id=client_id,
            client_secret=client_secret,
            authorize_endpoint=authorize_endpoint,
            token_endpoint=token_endpoint,
            refresh_token_endpoint=refresh_token_endpoint,
            revoke_token_endpoint=revoke_token_endpoint,
        )

        # Store metadata in session state for later use
        if 'oidc_metadata' not in st.session_state:
            st.session_state.oidc_metadata = oidc_metadata

        return oauth2

    except KeyError as e:
        logger.error(f"Missing configuration in secrets.toml: {str(e)}")
        st.error(f"Configuration error: Missing {str(e)} in secrets.toml")
        st.stop()
    except Exception as e:
        logger.error(f"Failed to initialize OAuth component: {str(e)}")
        st.error(f"Authentication initialization failed: {str(e)}")
        st.stop()


def get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """
    Fetch user information from the OIDC userinfo endpoint.

    Args:
        access_token: The OAuth2 access token

    Returns:
        Dictionary containing user information or None if failed
    """
    try:
        if 'oidc_metadata' not in st.session_state:
            logger.error("OIDC metadata not found in session state")
            return None

        userinfo_endpoint = st.session_state.oidc_metadata.get_userinfo_endpoint()

        if not userinfo_endpoint:
            logger.warning("Userinfo endpoint not available in OIDC metadata")
            logger.warning("This may indicate NASA Launchpad doesn't provide a userinfo endpoint")
            return None

        logger.info(f"Fetching user info from: {userinfo_endpoint}")

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(userinfo_endpoint, headers=headers, timeout=10)

        logger.info(f"Userinfo response status: {response.status_code}")

        response.raise_for_status()

        user_info = response.json()
        logger.info(f"Successfully fetched user information: {list(user_info.keys())}")
        return user_info

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching user info: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching user info: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching user info: {type(e).__name__}: {str(e)}")
        return None


def decode_id_token(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Decode the JWT id_token to extract user claims.

    Note: This decodes without verification since we trust the token from NASA Launchpad.
    In production, you should verify the signature using NASA's public keys (JWKS).

    Args:
        id_token: The JWT id_token from OAuth response

    Returns:
        Dictionary containing user claims or None if decoding fails
    """
    try:
        # Decode without verification (we trust NASA Launchpad as the issuer)
        # For production, use verify=True with jwks_uri from OIDC metadata
        decoded = jwt.decode(id_token, options={"verify_signature": False})
        logger.info(f"Successfully decoded id_token. Claims: {list(decoded.keys())}")
        return decoded
    except jwt.InvalidTokenError as e:
        logger.error(f"Failed to decode id_token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding id_token: {type(e).__name__}: {str(e)}")
        return None


def get_user_info_from_token(token_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract user information from OAuth token response.

    Tries multiple methods:
    1. Call userinfo endpoint with access_token
    2. If that fails or returns minimal data, decode id_token

    Args:
        token_response: Full OAuth token response including id_token and access_token

    Returns:
        Dictionary containing user information
    """
    user_info = None

    # Method 1: Try userinfo endpoint
    access_token = token_response.get('access_token')
    if access_token:
        user_info = get_user_info(access_token)

    # Check if userinfo endpoint returned useful data
    if user_info and len(user_info) > 1:  # More than just 'sub'
        logger.info("Using user info from userinfo endpoint")
        return user_info

    # Method 2: Decode id_token (NASA Launchpad ADFS likely has user claims here)
    id_token = token_response.get('id_token')
    if id_token:
        logger.info("Userinfo endpoint returned minimal data, decoding id_token instead")
        id_token_claims = decode_id_token(id_token)

        if id_token_claims:
            # Merge with any existing user_info (to keep 'sub' if present)
            if user_info:
                user_info.update(id_token_claims)
            else:
                user_info = id_token_claims

            logger.info(f"Extracted user info from id_token: {list(user_info.keys())}")
            return user_info

    # Fallback: Return whatever we got, even if minimal
    logger.warning("Could not extract comprehensive user info. Returning minimal data.")
    return user_info or {'sub': 'unknown'}


def check_authentication() -> bool:
    """
    Check if the user is authenticated.

    Returns:
        True if authenticated, False otherwise
    """
    return 'token' in st.session_state and st.session_state.token is not None


def logout():
    """Clear authentication session state."""
    logger.info("Logging out user")

    # Clear all authentication-related session state
    keys_to_clear = ['token', 'user_info', 'access_token']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


def display_user_info():
    """Display user information in the sidebar."""
    if 'user_info' in st.session_state and st.session_state.user_info:
        user_info = st.session_state.user_info

        with st.sidebar:
            st.markdown("---")
            st.markdown("### User Information")

            # Display name (check multiple possible claim names)
            name = (user_info.get('name') or
                   user_info.get('unique_name') or
                   user_info.get('given_name'))
            if name:
                st.markdown(f"**Name:** {name}")

            # Display email (check multiple possible claim names)
            email = (user_info.get('email') or
                    user_info.get('upn'))  # UPN is often email in ADFS
            if email:
                st.markdown(f"**Email:** {email}")

            # Display username (check multiple possible claim names)
            username = (user_info.get('preferred_username') or
                       user_info.get('unique_name') or
                       user_info.get('upn'))
            if username and username != email:  # Don't show if same as email
                st.markdown(f"**Username:** {username}")

            # Display sub (subject identifier) if nothing else is available
            if not (name or email or username):
                st.markdown(f"**User ID:** {user_info.get('sub', 'Unknown')}")

            # Logout button
            if st.button("Logout", key="logout_button", use_container_width=True):
                logout()
