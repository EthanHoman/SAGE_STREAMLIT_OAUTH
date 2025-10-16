"""
Authentication module for SAGE - NASA Launchpad OIDC Integration
"""

import streamlit as st
import requests
import logging
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
            logger.warning("Userinfo endpoint not available")
            return None

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(userinfo_endpoint, headers=headers, timeout=10)
        response.raise_for_status()

        user_info = response.json()
        logger.info("Successfully fetched user information")
        return user_info

    except Exception as e:
        logger.error(f"Failed to fetch user info: {str(e)}")
        return None


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

            # Display common user attributes
            if 'name' in user_info:
                st.markdown(f"**Name:** {user_info['name']}")
            if 'email' in user_info:
                st.markdown(f"**Email:** {user_info['email']}")
            if 'preferred_username' in user_info:
                st.markdown(f"**Username:** {user_info['preferred_username']}")

            # Logout button
            if st.button("Logout", key="logout_button", use_container_width=True):
                logout()
