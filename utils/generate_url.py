from fastapi import Request

def build_pagination_urls(request: Request, offset: int, limit: int, total: int):
    current_page_url = str(request.url.replace_query_params(offset=offset, limit=limit))
    
    next_offset = offset + limit
    prev_offset = offset - limit
    
    next_page_url = str(request.url.replace_query_params(offset=next_offset, limit=limit)) if next_offset < total else None
    prev_page_url = str(request.url.replace_query_params(offset=prev_offset, limit=limit)) if prev_offset >= 0 else None
    
    return current_page_url, next_page_url, prev_page_url
