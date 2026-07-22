import streamlit as st
from urllib.parse import urlparse
from core.models import Tenant
from core.auth import doc_to_dict

def get_current_subdomain() -> str | None:
    """
    Parses st.context.url to identify if a tenant subdomain is being accessed.
    Example: 
      - http://hooli.localhost:8501/ -> 'hooli'
      - http://localhost:8501/ -> None
    """
    try:
        url = st.context.url
        if not url:
            return None
        # Extract host and remove port, e.g. 'hooli.localhost:8501' -> 'hooli.localhost'
        host = urlparse(url).netloc.split(':')[0]
        parts = host.split('.')
        
        if 'localhost' in host:
            # For localhost development, if we have more than 1 part (e.g. hooli.localhost), return parts[0]
            if len(parts) > 1 and parts[-1] == 'localhost':
                return parts[0]
            return None
        else:
            # Production domain e.g. hooli.misportal.com (base domain misportal.com has 2 parts)
            # If parts is ['hooli', 'misportal', 'com'], length is 3, return parts[0]
            if len(parts) > 2:
                return parts[0]
            return None
    except Exception:
        return None

def get_tenant_by_subdomain(subdomain: str) -> dict | None:
    """Query tenant settings by its unique slug/subdomain."""
    tenant = Tenant.objects(slug=subdomain.lower().strip()).first()
    return doc_to_dict(tenant)
